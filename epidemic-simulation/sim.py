"""Stochastic SEIRV with Poisson tau-leaping.

Vectorized across replicates so a 100-run ensemble is one NumPy array
update per tau step, not a Python loop per run. Keeps Pyodide snappy
even for n_runs = 300.

Recording continues past E == I == 0 on purpose: every trajectory ends
up on the same time axis, so quantile bands across runs are a single
np.quantile call.
"""

import numpy as np

# Disease parameters come from the JS caller, but these defaults are
# the single source of truth if anyone imports sim.py standalone.
DISEASES = {
    "measles": {"R0": 15.0, "sigma": 1 / 10, "gamma": 1 / 8, "ve": 0.97, "coverage_key": "mmr"},
    "flu":     {"R0":  1.5, "sigma": 1 /  2, "gamma": 1 /  4, "ve": 0.45, "coverage_key": "flu"},
}


def _run_ensemble(N, I0, R0, sigma, gamma, ve, coverage, n_runs, tmax, tau, seed):
    """Run n_runs independent trajectories in lockstep.

    Returns (t, I_traj, cum_inc_final) where I_traj is shape (n_steps, n_runs).
    """
    rng = np.random.default_rng(seed)
    beta = R0 * gamma

    # V counts only the genuinely protected. Vaccine failures land in S
    # and get infected like anyone else. This is what makes ve < 1
    # actually matter for herd-immunity math.
    V = int(round(N * coverage * ve))
    S0 = N - V - I0

    S = np.full(n_runs, S0, dtype=np.int64)
    E = np.zeros(n_runs, dtype=np.int64)
    I = np.full(n_runs, I0, dtype=np.int64)
    R = np.zeros(n_runs, dtype=np.int64)
    cum_inc = np.full(n_runs, I0, dtype=np.int64)

    n_steps = int(tmax / tau) + 1
    t = np.linspace(0.0, n_steps * tau, n_steps + 1)
    I_traj = np.empty((n_steps + 1, n_runs), dtype=np.int64)
    I_traj[0] = I

    for k in range(1, n_steps + 1):
        # Frequency-dependent mixing: dividing by N (not S+E+I+R) lets
        # vaccinated individuals dilute contacts, which is how herd
        # immunity actually arises mechanically in this model.
        lam_SE = beta * S * I / N
        lam_EI = sigma * E
        lam_IR = gamma * I

        n_SE = rng.poisson(lam_SE * tau)
        n_EI = rng.poisson(lam_EI * tau)
        n_IR = rng.poisson(lam_IR * tau)

        # Clamping to current compartment sizes prevents tau-leaping
        # from taking more people than exist. The classic fix; without
        # it you occasionally get negative S in high-rate regimes.
        n_SE = np.minimum(n_SE, S)
        n_EI = np.minimum(n_EI, E)
        n_IR = np.minimum(n_IR, I)

        S = S - n_SE
        E = E + n_SE - n_EI
        I = I + n_EI - n_IR
        R = R + n_IR
        cum_inc = cum_inc + n_SE

        I_traj[k] = I

    return t, I_traj, cum_inc.astype(np.float64)


def simulate_state(disease, coverage_pct, N, I0, n_runs, tmax, tau, seed):
    """Run the ensemble for a single state and return summary arrays.

    coverage_pct is 0-100 (what data.js stores), converted to 0-1 here.
    Summary arrays are what the UI actually plots: median I, 2.5/97.5
    quantile band, and the attack-rate distribution. Raw trajectories
    stay on the Python side to keep the JS bridge payload small.
    """
    params = DISEASES[disease]
    coverage = coverage_pct / 100.0

    t, I_traj, cum_inc = _run_ensemble(
        N=N,
        I0=I0,
        R0=params["R0"],
        sigma=params["sigma"],
        gamma=params["gamma"],
        ve=params["ve"],
        coverage=coverage,
        n_runs=n_runs,
        tmax=tmax,
        tau=tau,
        seed=seed,
    )

    # Quantiles along the replicate axis give the uncertainty band that
    # readers actually care about. Single draws look wildly noisy and
    # mislead about the distribution of outcomes.
    I_med = np.median(I_traj, axis=1)
    I_lo = np.quantile(I_traj, 0.025, axis=1)
    I_hi = np.quantile(I_traj, 0.975, axis=1)

    attack_rate = cum_inc / N
    # Fade-out is an emergent property of stochastic dynamics. Below
    # ~2% attack rate the outbreak effectively never took off; worth
    # reporting separately from the median because it is bimodal.
    fadeout_frac = float(np.mean(attack_rate < 0.02))

    R_eff0 = params["R0"] * (1.0 - coverage * params["ve"])

    return {
        "t": t.tolist(),
        "I_med": I_med.tolist(),
        "I_lo": I_lo.tolist(),
        "I_hi": I_hi.tolist(),
        "attack_rate": attack_rate.tolist(),
        "attack_rate_median": float(np.median(attack_rate)),
        "fadeout_frac": fadeout_frac,
        "R_eff0": float(R_eff0),
        "R0": float(params["R0"]),
        "coverage": float(coverage),
        "ve": float(params["ve"]),
    }
