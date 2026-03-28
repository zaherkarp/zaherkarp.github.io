import { useState, useCallback, useRef, useEffect } from "react";
import { callApi, type ApiRequest, type ApiResult } from "../lib/skillsprout-api";
import { listOccupations } from "../lib/skillsprout-engine";
import type { TrajectoryResponse, TransitionMatch } from "../lib/skillsprout-engine";
import { testCases, runTestCase, type TestResult } from "../data/skillsprout-test-cases";

const ACCENT = "#3b82f6";

const allOccupations = listOccupations();

// ── Subcomponents ──────────────────────────────────────────────────

function MatchCard({ match, index }: { match: TransitionMatch; index: number }) {
  const [expanded, setExpanded] = useState(false);
  const categoryColors = {
    ready_now: { bg: "#059669", label: "Ready Now" },
    trainable: { bg: "#d97706", label: "Trainable" },
    long_term_reskill: { bg: "#7c3aed", label: "Long-Term Reskill" },
  };
  const cat = categoryColors[match.category];
  const zoneDeltaLabel = match.zoneDelta > 0 ? `+${match.zoneDelta}` : match.zoneDelta === 0 ? "same" : `${match.zoneDelta}`;

  return (
    <div
      className="match-card"
      style={{ animationDelay: `${index * 60}ms` }}
    >
      <div className="match-card-header" onClick={() => setExpanded(!expanded)}>
        <div className="match-card-title-row">
          <span className="match-category-badge" style={{ backgroundColor: cat.bg }}>
            {cat.label}
          </span>
          <span className="match-title">{match.occupation.title}</span>
        </div>
        <div className="match-card-stats">
          <span className="match-score" title="Skill overlap score">
            {(match.overlapScore * 100).toFixed(0)}% match
          </span>
          <span className="match-zone" title="Job Zone delta">
            Zone {zoneDeltaLabel}
          </span>
          <span className="match-expand">{expanded ? "▲" : "▼"}</span>
        </div>
      </div>

      {expanded && (
        <div className="match-card-details">
          <div className="match-meta-row">
            <span>O*NET: {match.occupation.code}</span>
            <span>Zone {match.occupation.zone}</span>
            <span>{match.occupation.category}</span>
          </div>

          <div className="match-section">
            <h5>Shared Skills ({match.sharedSkills.length})</h5>
            <div className="skill-tags">
              {match.sharedSkills.map(s => (
                <span key={s} className="skill-tag shared">{s}</span>
              ))}
            </div>
          </div>

          {match.missingSkills.length > 0 && (
            <div className="match-section">
              <h5>Skill Gaps ({match.missingSkills.length})</h5>
              <div className="skill-tags">
                {match.missingSkills.map(g => (
                  <span key={g.skill} className={`skill-tag gap gap-${g.importance}`}>
                    {g.skill}
                    <span className="gap-badge">{g.importance === "critical" ? "!" : g.importance === "important" ? "•" : "○"}</span>
                  </span>
                ))}
              </div>
            </div>
          )}

          {match.trainingPaths.length > 0 && (
            <div className="match-section">
              <h5>Training Paths</h5>
              <div className="training-paths">
                {match.trainingPaths.map(tp => (
                  <div key={tp.skill} className="training-path-item">
                    <span className="tp-skill">{tp.skill}</span>
                    <span className="tp-months">~{tp.estimatedMonths}mo</span>
                    <span className="tp-resources">{tp.resources.join(", ")}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ApiLog({ entries }: { entries: ApiLogEntry[] }) {
  const logRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [entries]);

  return (
    <div className="api-log" ref={logRef}>
      <div className="api-log-header">
        <span className="api-log-dot" />
        <span className="api-log-dot yellow" />
        <span className="api-log-dot green" />
        <span className="api-log-title">api_session.log</span>
      </div>
      <div className="api-log-body">
        {entries.map((entry, i) => (
          <div key={i} className={`api-log-entry ${entry.type}`}>
            <span className="api-log-prefix">
              {entry.type === "request" ? "→ REQ" : entry.type === "response" ? "← RES" : "  #"}
            </span>
            <span className="api-log-text">{entry.text}</span>
          </div>
        ))}
        {entries.length === 0 && (
          <div className="api-log-entry comment">
            <span className="api-log-prefix">  #</span>
            <span className="api-log-text">Select an occupation and click Search to begin</span>
          </div>
        )}
      </div>
    </div>
  );
}

interface ApiLogEntry {
  type: "request" | "response" | "comment";
  text: string;
}

// ── Test Suite Runner ──────────────────────────────────────────────

function TestSuiteRunner() {
  const [results, setResults] = useState<TestResult[]>([]);
  const [running, setRunning] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [filterTheme, setFilterTheme] = useState<string>("all");

  const themes = ["all", ...new Set(testCases.map(tc => tc.theme))];

  const handleRun = () => {
    setRunning(true);
    setExpanded(true);
    // Run async-ish to let UI update
    setTimeout(() => {
      const res = testCases.map(runTestCase);
      setResults(res);
      setRunning(false);
    }, 50);
  };

  const passed = results.filter(r => r.passed).length;
  const failed = results.filter(r => !r.passed).length;
  const filtered = filterTheme === "all"
    ? results
    : results.filter(r => {
        const tc = testCases.find(t => t.id === r.id);
        return tc?.theme === filterTheme;
      });

  return (
    <div className="ss-test-suite">
      <div className="ss-test-header" onClick={() => setExpanded(!expanded)}>
        <h4>
          Test Suite
          {results.length > 0 && (
            <span className={`ss-test-badge ${failed === 0 ? "pass" : "fail"}`}>
              {passed}/{results.length} passed
            </span>
          )}
        </h4>
        <div className="ss-test-actions">
          <button
            className="ss-btn ss-btn-primary"
            onClick={(e) => { e.stopPropagation(); handleRun(); }}
            disabled={running}
          >
            {running ? "Running..." : `Run ${testCases.length} Tests`}
          </button>
          <span className="match-expand">{expanded ? "▲" : "▼"}</span>
        </div>
      </div>

      {expanded && results.length > 0 && (
        <div className="ss-test-body">
          <div className="ss-test-themes">
            {themes.map(theme => (
              <button
                key={theme}
                className={`ss-filter-tab ${filterTheme === theme ? "active" : ""}`}
                onClick={() => setFilterTheme(theme)}
              >
                {theme === "all" ? "All" : theme}
              </button>
            ))}
          </div>

          <div className="ss-test-results">
            {filtered.map(r => {
              const tc = testCases.find(t => t.id === r.id);
              return (
                <div key={r.id} className={`ss-test-row ${r.passed ? "pass" : "fail"}`}>
                  <span className="ss-test-icon">{r.passed ? "✓" : "✗"}</span>
                  <div className="ss-test-info">
                    <span className="ss-test-id">[{r.id}]</span>
                    <span className="ss-test-name">{r.name}</span>
                    {!r.passed && r.failures.map((f, i) => (
                      <div key={i} className="ss-test-failure">↳ {f}</div>
                    ))}
                    {tc && <div className="ss-test-desc">{tc.description}</div>}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Main Component ─────────────────────────────────────────────────

export default function SkillSproutDemo() {
  const [occupation, setOccupation] = useState("");
  const [additionalSkills, setAdditionalSkills] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<"all" | "ready_now" | "trainable" | "long_term_reskill">("all");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [result, setResult] = useState<TrajectoryResponse | null>(null);
  const [apiLog, setApiLog] = useState<ApiLogEntry[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [hasMore, setHasMore] = useState(false);
  const [turn, setTurn] = useState(0);
  const [showOccList, setShowOccList] = useState(false);
  const [searchFilter, setSearchFilter] = useState("");

  const addLog = useCallback((entry: ApiLogEntry) => {
    setApiLog(prev => [...prev, entry]);
  }, []);

  const doApiCall = useCallback((req: ApiRequest) => {
    // Log request
    const reqSummary = `action=${req.action}` +
      (req.occupation ? ` occ="${req.occupation}"` : "") +
      (req.additionalSkills?.length ? ` +skills=[${req.additionalSkills.join(",")}]` : "") +
      (req.categoryFilter && req.categoryFilter !== "all" ? ` filter=${req.categoryFilter}` : "");

    setApiLog(prev => [...prev, { type: "request", text: reqSummary }]);

    const apiResult = callApi(req);

    // Update state
    setSessionId(apiResult.sessionId);
    setTurn(apiResult.turn);
    setHasMore(apiResult.meta.hasMore);
    setSuggestions(apiResult.meta.suggestions);

    if ("readyNow" in apiResult.data) {
      const data = apiResult.data as TrajectoryResponse;
      setResult(data);

      const total = data.readyNow.length + data.trainable.length + data.longTermReskill.length;
      const resSummary = data.success
        ? `turn=${apiResult.turn} matches=${total} (ready=${data.readyNow.length} train=${data.trainable.length} reskill=${data.longTermReskill.length})` +
          (apiResult.meta.hasMore ? " [more available]" : "")
        : `error: ${data.error}`;

      setApiLog(prev => [...prev, { type: "response", text: resSummary }]);
    } else if ("message" in apiResult.data) {
      setApiLog(prev => [...prev, { type: "response", text: (apiResult.data as { message: string }).message }]);
      setResult(null);
    }

    return apiResult;
  }, []);

  const handleSearch = () => {
    if (!occupation.trim()) return;
    const skills = additionalSkills.trim()
      ? additionalSkills.split(",").map(s => s.trim()).filter(Boolean)
      : undefined;

    doApiCall({
      action: "search",
      sessionId: sessionId ?? undefined,
      occupation: occupation.trim(),
      additionalSkills: skills,
      categoryFilter,
      maxPerCategory: 5,
    });
  };

  const handleMore = () => {
    doApiCall({
      action: "more",
      sessionId: sessionId ?? undefined,
      occupation: occupation.trim(),
      categoryFilter,
      maxPerCategory: 5,
    });
  };

  const handleFilter = (cat: "all" | "ready_now" | "trainable" | "long_term_reskill") => {
    setCategoryFilter(cat);
    doApiCall({
      action: "filter",
      sessionId: sessionId ?? undefined,
      occupation: occupation.trim(),
      categoryFilter: cat,
      maxPerCategory: 10,
    });
  };

  const handleAddSkills = () => {
    if (!additionalSkills.trim()) return;
    const skills = additionalSkills.split(",").map(s => s.trim()).filter(Boolean);
    doApiCall({
      action: "add_skills",
      sessionId: sessionId ?? undefined,
      occupation: occupation.trim(),
      additionalSkills: skills,
      categoryFilter,
    });
  };

  const handleReset = () => {
    if (sessionId) {
      doApiCall({ action: "reset", sessionId });
    }
    setResult(null);
    setOccupation("");
    setAdditionalSkills("");
    setCategoryFilter("all");
    setSuggestions([]);
    setHasMore(false);
  };

  const handleSelectOccupation = (title: string) => {
    setOccupation(title);
    setShowOccList(false);
    setSearchFilter("");
  };

  const filteredOccupations = searchFilter.trim()
    ? allOccupations.filter(o =>
        o.title.toLowerCase().includes(searchFilter.toLowerCase()) ||
        o.category.toLowerCase().includes(searchFilter.toLowerCase())
      )
    : allOccupations;

  const allMatches: TransitionMatch[] = result
    ? [...result.readyNow, ...result.trainable, ...result.longTermReskill]
    : [];

  return (
    <div className="ss-demo">
      {/* Controls */}
      <div className="ss-controls">
        <div className="ss-input-group">
          <label className="ss-label">Current Occupation</label>
          <div className="ss-input-row">
            <input
              type="text"
              className="ss-input"
              placeholder="e.g., Software Developer, Registered Nurse..."
              value={occupation}
              onChange={e => setOccupation(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSearch()}
            />
            <button
              className="ss-btn ss-btn-browse"
              onClick={() => setShowOccList(!showOccList)}
              title="Browse occupations"
            >
              ☰
            </button>
          </div>

          {showOccList && (
            <div className="ss-occ-dropdown">
              <input
                type="text"
                className="ss-occ-search"
                placeholder="Filter occupations..."
                value={searchFilter}
                onChange={e => setSearchFilter(e.target.value)}
                autoFocus
              />
              <div className="ss-occ-list">
                {filteredOccupations.map(o => (
                  <button
                    key={o.code}
                    className="ss-occ-item"
                    onClick={() => handleSelectOccupation(o.title)}
                  >
                    <span className="ss-occ-title">{o.title}</span>
                    <span className="ss-occ-cat">{o.category}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="ss-input-group">
          <label className="ss-label">Additional Skills (comma-separated)</label>
          <div className="ss-input-row">
            <input
              type="text"
              className="ss-input"
              placeholder="e.g., python, docker, project management..."
              value={additionalSkills}
              onChange={e => setAdditionalSkills(e.target.value)}
            />
            {additionalSkills.trim() && result && (
              <button className="ss-btn ss-btn-add" onClick={handleAddSkills} title="Add skills and re-run">
                + Add
              </button>
            )}
          </div>
        </div>

        <div className="ss-actions">
          <button className="ss-btn ss-btn-primary" onClick={handleSearch}>
            Search Trajectories
          </button>
          {result && (
            <button className="ss-btn ss-btn-secondary" onClick={handleReset}>
              Reset
            </button>
          )}
        </div>

        {/* Category filter tabs */}
        {result && result.success && (
          <div className="ss-filter-tabs">
            {([
              ["all", "All"],
              ["ready_now", `Ready Now (${result.readyNow.length})`],
              ["trainable", `Trainable (${result.trainable.length})`],
              ["long_term_reskill", `Long-Term Reskill (${result.longTermReskill.length})`],
            ] as const).map(([key, label]) => (
              <button
                key={key}
                className={`ss-filter-tab ${categoryFilter === key ? "active" : ""}`}
                onClick={() => handleFilter(key)}
              >
                {label}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Results */}
      {result && result.success && (
        <div className="ss-results">
          <div className="ss-results-header">
            <h3>
              Trajectories from <strong>{result.source?.title}</strong>
            </h3>
            <span className="ss-turn-badge">Turn {turn}</span>
          </div>

          {result.source && (
            <div className="ss-source-skills">
              <span className="ss-source-label">Your skills:</span>
              {result.sourceSkills.map(s => (
                <span key={s} className="skill-tag source">{s}</span>
              ))}
            </div>
          )}

          {allMatches.length === 0 ? (
            <div className="ss-no-results">
              No matches found for this configuration. Try adjusting filters or adding skills.
            </div>
          ) : (
            <div className="ss-match-list">
              {allMatches.map((m, i) => (
                <MatchCard key={m.occupation.code} match={m} index={i} />
              ))}
            </div>
          )}

          {hasMore && (
            <button className="ss-btn ss-btn-more" onClick={handleMore}>
              Load More Results
            </button>
          )}

          {suggestions.length > 0 && (
            <div className="ss-suggestions">
              <h4>Suggestions</h4>
              <ul>
                {suggestions.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Error state */}
      {result && !result.success && (
        <div className="ss-error">
          <p>{result.error}</p>
          {result.suggestions.map((s, i) => (
            <p key={i} className="ss-error-suggestion">{s}</p>
          ))}
        </div>
      )}

      {/* API Log */}
      <ApiLog entries={apiLog} />

      {/* Test Suite Runner */}
      <TestSuiteRunner />

      {/* Attribution */}
      <div className="ss-attribution">
        <p>
          Full O*NET 28.3 database ({allOccupations.length.toLocaleString()} occupations, 65 skill/knowledge dimensions) from{" "}
          <a href="https://www.onetcenter.org/database.html" target="_blank" rel="noopener noreferrer">O*NET Resource Center</a>{" "}
          (CC BY 4.0). Transition framework informed by{" "}
          <a href="https://www.anthropic.com/research/the-macroeconomic-impact-of-artificial-intelligence" target="_blank" rel="noopener noreferrer">
            Anthropic's AI economic impact research
          </a>{" "}
          on skill-based labor transitions.
          All matching runs client-side — no data leaves your browser.
        </p>
      </div>
    </div>
  );
}
