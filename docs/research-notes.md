# Research notes — verified citations (Oct 19, 2026)

All six papers below were opened and checked: author list, year, venue, and
the exact claim attributed. Status is final unless noted.

## Verified

- [x] **Wares, S., Isaacs, J., & Elyan, E. (2019).** Data stream mining:
  Methods and challenges for handling concept drift. *SN Applied Sciences*,
  1(11), 1412. https://doi.org/10.1007/s42452-019-1433-0
  The conclusion literally enumerates the four shortcomings: *"1. Outdated
  state-of-the-art drift detection methods. 2. A lack of benchmark datasets
  for evaluation. 3. Flawed evaluation metrics, including an over-reliance
  on classifier accuracy. 4. The inability of drift detectors to cope with
  additional data anomalies, such as temporal dependence."* Strongest
  citation in the set — direct quote.

- [x] **Bifet, A. (2017).** Classifier concept drift detection and the
  illusion of progress. In *Proc. ICAISC 2017, Part II* (pp. 715–725).
  Springer.
  Author's own summary: *"the surprising result that non-change detectors
  can outperform change-detectors when used in a classification streaming
  evaluation… evaluation of change detectors should not be done using only
  classifiers."* Classifier accuracy misleads; temporal dependence is
  implicated. Wares (2019) independently cites this result.

- [x] **Barddal, J. P., Gomes, H. M., Enembreck, F., & Pfahringer, B.
  (2017).** A survey on feature drift adaptation: Definition, benchmark,
  challenges and future directions. *Journal of Systems and Software*, 127,
  278–294. https://doi.org/10.1016/j.jss.2016.07.005
  The survey's premise is that feature drift lacks formalization, benchmarks
  and assessment procedures. Safe README phrasing: "feature drift has
  received little attention relative to other drift types (Barddal et al.,
  2017)." (An earlier conference version appeared at ICTAI 2015.)

- [x] **Lukats, D., Zielinski, O., Hahn, A., & Stahl, F. (2024).** A
  benchmark and survey of fully unsupervised concept drift detectors on
  real-world data streams. *International Journal of Data Science and
  Analytics*. https://doi.org/10.1007/s41060-024-00620-y
  Note: year is **2024, not 2025**. Ten algorithms reviewed, seven evaluated
  on eleven real-world streams; *"reveals issues with the evaluation metrics
  Mean Time Ratio and lift-per-drift"* and highlights open research
  challenges. It does **not** make the classifier-accuracy argument — do not
  conflate it with Komorniczak (2026) or Bifet (2017).

- [x] **Komorniczak, J. (2026).** How well does Classification Accuracy
  capture Concept Drift Detection Quality? An overview of Concept Drift
  Detection evaluation. *arXiv:2605.31186*. [Preprint — not peer-reviewed]
  *"The experiments confirmed that accuracy is not a reliable proxy for
  drift detection quality"*; *"maximizing accuracy can lead to poor drift
  detection performance."* This — not Lukats — is the source for the
  accuracy-misleads finding.

- [x] **Cerqueira, V., Gomes, H. M., Heyden, M., Pfahringer, B., & Bifet, A.
  (2026).** A Framework for Evaluating and Benchmarking Concept Drift
  Detection Methods. *arXiv:2606.07789*. [Preprint — not peer-reviewed]
  Content verified: injects controlled distributional changes into
  real-world datasets via Monte Carlo trials; timing-aware evaluation
  protocol (F1 detection score, normalized detection time); benchmarks 14
  detectors on 7 datasets across 4 drift types, abrupt and gradual.
  **Venue unconfirmed — never label this "KDD 2026".**

## Corrections made during verification

- Lukats year corrected: 2024, not 2025.
- The classifier-accuracy finding belongs to Komorniczak (2026) and Bifet
  (2017), not Lukats.
- Cerqueira et al. venue unconfirmed; cited as arXiv preprint only.
- Barddal "neglected" claim softened to "received little attention" per the
  survey's actual framing.
