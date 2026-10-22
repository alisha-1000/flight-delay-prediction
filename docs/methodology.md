# Methodology (Theoretical Rigor)

TODO: write the theory you will be asked about in the viva.

## Logistic Regression
- [ ] Model, log-loss objective, L2 regularisation, interpretation of coefficients
- [ ] Why scaling and one-hot encoding are needed

## XGBoost
- [ ] Additive tree boosting, second-order Taylor approximation of the loss
- [ ] Regularisation (gamma, lambda, depth), shrinkage, subsampling
- [ ] Handling class imbalance (`scale_pos_weight`) and its effect on calibration

## Calibration
- [ ] Reliability diagrams, ECE, Brier score
- [ ] Platt scaling vs. isotonic regression; fit on validation split only

## Evaluation
- [ ] Why PR AUC is primary under imbalance
- [ ] Choosing the operational precision threshold
- [ ] Chronological split and why random K-fold leaks
