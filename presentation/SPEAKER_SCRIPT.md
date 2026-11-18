# English presentation script

Provisional delivery length: 15–18 minutes, 17 slides. No formal duration was included in the supplied local pack; adjust to the assigned seminar slot.

## Slide 1: Periodic advection: accuracy and fidelity

Today we use periodic advection to examine when a numerical evolution is trustworthy. The exact solution translates without changing its shape, giving precise tests for damping, phase error and oscillation. Group C compares two verified baselines with an MC flux-limited extension. Our principal finding is that amplitude, phase, total variation and computational cost lead to different choices. The AI audit records how the material was checked, and each member will complete their own contribution statement from actual work.

## Slide 2: Research question and controlled model

The domain has unit length, the baseline speed is one, and one unit of time is a complete transit. We store point values, not cell averages, and use the same convention for the exact reference. The sine isolates a mode. The smooth packet places its maximum at the seam, testing periodic wrap-around. The square exposes smearing and ripples. There is no physical diffusion in this model.

## Slide 3: Baseline updates from the PDE

Upwind follows the direction from which information arrives. At a Courant number between zero and one it is a convex average of the current and upstream values. Lax–Wendroff keeps the second temporal Taylor term and replaces the second time derivative through the PDE. Its centered spatial differences make it second-order accurate on smooth hyperbolic refinement families. Both updates telescope in conservative form.

## Slide 4: Diffusion and dispersion have different mechanisms

The modified equation makes the leading defects explicit. Upwind adds an artificial diffusion term. Lax–Wendroff has a leading third derivative, which changes phase and is dispersive. The negative right-neighbour weight explains why a bounded computation can exceed the initial range. These smooth expansions explain mechanisms; we do not apply them as pointwise Taylor formulas at a discontinuity.

## Slide 5: MC limits the antidiffusive correction

The flux contains the robust upwind part and a limited fraction of the higher-order correction. MC is the main choice because near equal consecutive slopes it uses the central slope, whereas Minmod is more restrictive. We compute the limited product with signed minima, so a zero denominator never produces an arbitrary large ratio. The interface flux is shared by neighboring updates, preserving mass. LeVeque chapter six gives the corresponding construction.

## Slide 6: TVD proof applies to this complete update

The proof uses coefficient bounds for the precise fully discrete flux. Both limiters keep their value and their value divided by the ratio between zero and two. This places each effective coefficient between C squared and two C minus C squared. Taking adjacent differences and applying the triangle inequality proves nonincrease of total variation. We do not use a linear von Neumann factor as a nonlinear proof. TVD controls variation; it does not establish the smallest error.

## Slide 7: Linear Fourier factors and the CFL boundary

Each spatial shift of a Fourier mode multiplies it by an exponential. Substitution gives these factors directly. Because the periodic update matrices are circulant, the discrete Fourier transform diagonalizes them, and Parseval transfers the factor bounds to a norm bound. The coefficient, grid and boundary assumptions all match here. Above one, dangerous modes grow. Stability is a propagation bound and does not guarantee small error or freedom from ripples.

## Slide 8: Verification includes a hand-computable seam test

This small case checks every node, including the seam. For Lax–Wendroff the weights are three eighths, three quarters and minus one eighth. For MC only one limited jump survives. All three outputs sum to three. Two test expectations were initially entered incorrectly by the AI and failed. Explicit arithmetic corrected the expectations, with the update implementations unchanged. That history remains part of the audit. These are agent checks and still need student reproduction.

## Slide 9: Separated error needs a declared reference

This is the most delicate part of the study. A constant-Courant refinement changes both space and time, so it gives a joint rate. We use exact semidiscrete Fourier evolution to remove temporal error for the linear spatial study. For a fixed grid, classical Lax–Wendroff is not the Taylor integrator of the centered derivative matrix: its three-point second derivative differs from the square of that matrix. The resulting temporal discrepancy is generally first order. For MC we document a tolerance-refined limiting ODE reference and disclose the conditional nature of the separation.

## Slide 10: Measured refinement rates

The exact-in-time spatial study recovers the expected first and second orders for the linear operators. MC is closer to 1.73 in the measured global L2 norm, consistent with its local reduction near extrema. The temporal plot approaches first-order behavior relative to the stated small-step limits. Reference tolerance changes remain below one percent of the measured error. We preserve these observations instead of forcing an advertised second-order result for every method.

## Slide 11: Smooth profiles and discontinuities

The smooth packet and square expose different costs. Upwind spreads both. Lax–Wendroff gives a much sharper smooth packet but produces signed ripples around the square. MC removes these extrema within the measured tolerance and keeps the square sharper than upwind. For the square, maximum error near a moving jump need not vanish, so we also measure L1 convergence and physical transition width. A growing number of transition cells can coexist with a shrinking physical width.

## Slide 12: Dangerous-mode growth is distinct from ripples

Here the initial checkerboard deliberately excites the mode that challenges the CFL boundary. Above the bound, its amplitude grows as the analytic factor predicts, and the larger violation reaches the explicit safety stop. This growth is different from the bounded dispersive ripples of Lax–Wendroff at C equal to one half. At C equal to one both baselines give an exact represented shift, so that special configuration would conceal the ordinary accuracy tradeoff.

## Slide 13: Measured amplitude and numerical phase speed

The modal comparison distinguishes damping from speed. Upwind at C equal to one half retains the resolved phase while reducing amplitude. Lax–Wendroff damps long waves less but shifts their phase. MC is nonlinear, so its projected coefficient is an effective response and harmonics are also recorded. We omit speed claims when the remaining coefficient is below the declared reliability gate.

## Slide 14: Errors accumulated over ten periods

The long-time sine experiment makes accumulated defects visible. Upwind gradually loses amplitude. Lax–Wendroff preserves amplitude better but accumulates a phase defect. The limited solution also changes harmonics. We record intermediate times and unwrap phases at each step, so an integer number of phase turns cannot hide behind a return-time snapshot. Mass conservation persists even when the shape has changed.

## Slide 15: Mass conservation and total variation

All methods preserve the discrete mass to roundoff in the diagnostic sweep. Their total variation histories are very different. Lax–Wendroff generates extra variation around jumps, while MC satisfies the TVD inequality within the preregistered tolerance. Conservation therefore does not establish fidelity or accuracy. It is a necessary structural check for this periodic flux update, but it cannot distinguish a sharply resolved solution from a smeared or oscillatory one.

## Slide 16: Cost at predeclared accuracy targets

The horizontal axis is L1 error and the vertical axis is measured runtime. We compare configurations satisfying the same declared target, rather than comparing only a common grid. The packet targets are 0.02 and 0.005; the square targets are 0.05 and 0.02. Every target was achieved in the tested grid set. The ranking changes with the datum and target, and close timing differences should be treated cautiously. Grid updates provide a portable supplement, though MC costs more per update.

## Slide 17: Limitations and conclusion

The findings support a conditional choice of method. Upwind is robust but dissipative. Lax–Wendroff is accurate on smooth data but can violate range constraints at jumps. MC controls variation while paying in computation and local accuracy near extrema. These results apply to the declared linear periodic model and do not establish behavior for all nonlinear conservation laws. The next decisive check is an independent teammate environment reproduction, followed by viva preparation that establishes actual mathematical ownership.
