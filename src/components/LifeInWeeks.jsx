import { useState, useMemo } from "react";
import { BIRTH_DATE, LIFE_YEARS, EVENTS } from "../data/life-in-weeks.js";

const WEEKS_PER_YEAR = 52;
const TOTAL_WEEKS = LIFE_YEARS * WEEKS_PER_YEAR;

const MS_PER_WEEK = 7 * 24 * 60 * 60 * 1000;

function weekIndex(date) {
  return Math.floor((date - BIRTH_DATE) / MS_PER_WEEK);
}

export default function LifeInWeeks() {
  const [tooltip, setTooltip] = useState(null);

  const { currentWeekIdx, eventMap } = useMemo(() => {
    const now = new Date();
    const idx = weekIndex(now);
    const map = new Map();
    for (const evt of EVENTS) {
      const wi = weekIndex(new Date(evt.date));
      map.set(wi, evt.label);
    }
    return { currentWeekIdx: idx, eventMap: map };
  }, []);

  const birthYear = BIRTH_DATE.getFullYear();
  const ageYears = (currentWeekIdx / WEEKS_PER_YEAR).toFixed(1);
  const pctComplete = ((currentWeekIdx / TOTAL_WEEKS) * 100).toFixed(1);
  const weeksRemaining = TOTAL_WEEKS - currentWeekIdx;

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#F5F0E8",
        color: "#1A1814",
        fontFamily: "'Cormorant Garamond', serif",
        padding: "2rem",
      }}
    >
      <div style={{ maxWidth: 720, margin: "0 auto" }}>
        {/* Header */}
        <h1
          style={{
            fontSize: "2rem",
            fontWeight: 700,
            marginBottom: "0.25rem",
          }}
        >
          Life in Weeks
        </h1>
        <div
          style={{
            fontFamily: "'IBM Plex Mono', monospace",
            fontSize: "0.85rem",
            lineHeight: 1.7,
            marginBottom: "1.25rem",
            color: "#4A4438",
          }}
        >
          <div>Age: {ageYears} years</div>
          <div>
            Week {currentWeekIdx} of {TOTAL_WEEKS}
          </div>
          <div>{pctComplete}% complete</div>
          <div>{weeksRemaining} weeks remaining</div>
        </div>

        {/* Legend */}
        <div
          style={{
            display: "flex",
            gap: "1rem",
            flexWrap: "wrap",
            marginBottom: "1.5rem",
            fontFamily: "'IBM Plex Mono', monospace",
            fontSize: "0.75rem",
            color: "#4A4438",
          }}
        >
          {[
            { color: "#1A1814", border: "none", label: "Lived" },
            { color: "#B85C2A", border: "none", label: "Current week" },
            { color: "#7A5C1E", border: "none", label: "Event" },
            {
              color: "transparent",
              border: "1px solid #C5BBA8",
              label: "Future",
            },
          ].map((item) => (
            <div
              key={item.label}
              style={{ display: "flex", alignItems: "center", gap: 4 }}
            >
              <span
                style={{
                  display: "inline-block",
                  width: 10,
                  height: 10,
                  background: item.color,
                  border: item.border || "none",
                  borderRadius: 1,
                }}
              />
              {item.label}
            </div>
          ))}
        </div>

        {/* Grid */}
        <div style={{ position: "relative" }}>
          {Array.from({ length: LIFE_YEARS }, (_, yearIdx) => {
            const age = yearIdx;
            const calYear = birthYear + yearIdx;
            const showLabel = yearIdx % 5 === 0;
            const isDecadeEnd = yearIdx > 0 && yearIdx % 10 === 0;

            return (
              <div
                key={yearIdx}
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: isDecadeEnd ? 6 : 0,
                }}
              >
                {/* Row label */}
                <div
                  style={{
                    width: 80,
                    flexShrink: 0,
                    fontFamily: "'IBM Plex Mono', monospace",
                    fontSize: "0.6rem",
                    color: "#8A8070",
                    textAlign: "right",
                    paddingRight: 8,
                    visibility: showLabel ? "visible" : "hidden",
                  }}
                >
                  {age} / {calYear}
                </div>
                {/* Week boxes */}
                <div style={{ display: "flex", gap: 2 }}>
                  {Array.from({ length: WEEKS_PER_YEAR }, (_, weekIdx) => {
                    const wi = yearIdx * WEEKS_PER_YEAR + weekIdx;
                    const isEvent = eventMap.has(wi);
                    const isCurrent = wi === currentWeekIdx;
                    const isLived = wi < currentWeekIdx;

                    let bg, border;
                    if (isEvent) {
                      bg = "#7A5C1E";
                      border = "none";
                    } else if (isCurrent) {
                      bg = "#B85C2A";
                      border = "none";
                    } else if (isLived) {
                      bg = "#1A1814";
                      border = "none";
                    } else {
                      bg = "transparent";
                      border = "1px solid #C5BBA8";
                    }

                    const tooltipLabel = isEvent
                      ? eventMap.get(wi)
                      : isCurrent
                        ? `📍 Current week (week ${wi})`
                        : null;

                    return (
                      <div
                        key={wi}
                        style={{
                          width: 7,
                          height: 7,
                          background: bg,
                          border,
                          borderRadius: 1,
                          cursor: tooltipLabel ? "pointer" : "default",
                          position: "relative",
                        }}
                        onMouseEnter={(e) => {
                          if (tooltipLabel) {
                            const rect = e.currentTarget.getBoundingClientRect();
                            setTooltip({
                              text: tooltipLabel,
                              x: rect.left + rect.width / 2,
                              y: rect.top - 8,
                            });
                          }
                        }}
                        onMouseLeave={() => setTooltip(null)}
                      />
                    );
                  })}
                </div>
              </div>
            );
          })}

          {/* Tooltip */}
          {tooltip && (
            <div
              style={{
                position: "fixed",
                left: tooltip.x,
                top: tooltip.y,
                transform: "translate(-50%, -100%)",
                background: "#1A1814",
                color: "#F5F0E8",
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: "0.7rem",
                padding: "4px 8px",
                borderRadius: 4,
                whiteSpace: "nowrap",
                pointerEvents: "none",
                zIndex: 10,
              }}
            >
              {tooltip.text}
            </div>
          )}
        </div>

        {/* Footer */}
        <p
          style={{
            marginTop: "2rem",
            fontFamily: "'IBM Plex Mono', monospace",
            fontSize: "0.75rem",
            color: "#8A8070",
          }}
        >
          Birth year: 1985. Exact date withheld intentionally.
        </p>
      </div>
    </div>
  );
}
