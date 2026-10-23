# Theorem 004: Exact periodicity of every fixed right-edge diagonal

**Status:** Proven, independently computationally checked. **Not** a solution to any of the three Rule 30 Prize problems.

Let x(i,t) be Rule 30 started from a single active cell at i=0. For integer k>=0 define y_k(t)=x(t-k,t), t>=0. Then for every k>=0 and t>=0,

    y_k(t+2^k)=y_k(t).

The bound 2^k is not necessarily the minimal period.

## Proof
The rightmost occupied position is t and has state 1 for every t>=0, by finite propagation and induction: the rightmost new cell has predecessor triple (1,0,0), whose Rule 30 output is 1. Hence y_0(t)=1 for all t. Set y_{-1}(t)=0 (outside the light cone). Rule 30's local formula f(a,b,c)=a XOR (b OR c), applied at position t+1-k and time t+1, gives for k>=1:

    y_k(t+1)=y_k(t) XOR (y_{k-1}(t) OR y_{k-2}(t)).    (1)

For k=1, y_0=1 and y_{-1}=0, so y_1(t+1)=y_1(t) XOR 1; hence y_1 has period 2.

Assume k>=2 and, inductively, y_{k-1} and y_{k-2} have periods dividing 2^(k-1). Then q_k(t)=y_{k-1}(t) OR y_{k-2}(t) also has period dividing P=2^(k-1). Applying (1) for 2P consecutive steps gives

    y_k(t+2P) XOR y_k(t)
      = XOR_{j=0}^{2P-1} q_k(t+j)
      = (XOR_{j=0}^{P-1} q_k(t+j)) XOR
        (XOR_{j=0}^{P-1} q_k(t+P+j))
      = 0.

Thus y_k has period dividing 2P=2^k. Induction completes the proof. QED.

## CMCC interpretation
S: right-edge diagonal (k,t,bit); D: initial seed; L: diagonal predecessor offsets k,k-1,k-2; F: XOR/OR recurrence; A: XOR parity of a doubled period. The invariant is a theorem about Rule 30 and does not rely on the CMCC completeness conjecture.

## Implications and limitations
All diagonals at fixed distance k from the **right moving boundary** are periodic from t=0, even though the stationary center column is conjectured nonperiodic. The center at time t is y_t(t), so k is *not fixed*. Therefore the theorem does not imply periodicity of the center, nor any prize result. It does identify a triangular, exactly periodic subsystem and suggests testing if diagonal-period information can constrain center-column dynamics.

## Verification
`python experiment_v04.py` compares diagonal recurrence with an independent sparse full-lattice Rule 30 simulation for t=0..4096, k=0..12, and verifies predicted periods on the tested horizon. `results_v04.json` records empirical minimal periods. This verification supports but is not required for the proof.
