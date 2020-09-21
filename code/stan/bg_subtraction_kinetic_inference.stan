data {
    // Dimensional parameters  
    int<lower=1> J; // Number of unique time traces>
    int<lower=1> N; // Number of light-activated measurements
    int<lower=1, upper=J> idx[N]; // ID vector for individual traces

    // Kinetics data 
    vector[N] mcherry_int; // Observed mCherry intensity 
    real<lower=0> experiment_time[N]; // Time of experiment for gp subtraction
    vector<lower=0>[N] activation_time; // Relative time for activation
    vector<lower=0>[J] power_density;
    real<lower=0> micro_conc; // Concentration of micro
    int<lower=0, upper=N> timepoint_idx[J]; // Timepoints for which the background signal is used in calculation of fold-change

    // GP hyperparameters
    real preact_sd;
    real preact_mean;
    real alpha_mean;
    real rho_mean;
}

transformed data {
    matrix [N, N] cov = cov_exp_quad(experiment_time, alpha_mean, rho_mean);
    vector[N] gp_mu = rep_vector(0, N);
    matrix[N, N] L_cov;
    for (i in 1:N) {
      cov[i, i] = cov[i, i] + 1e-5;
    }
    L_cov = cholesky_decompose(cov);
 
}

parameters {
  // Kinetic Parameters 
  vector[N] eta;
  vector<lower=0>[J] kon;
  vector<lower=0>[J] saturation;
  real<lower=0> sigma;
  
  // model parameters
  real ep_ai;
  real<lower=0> theta_i;
  real<lower=0> theta_a;
  real<lower=0> fc_sigma;
  
}

transformed parameters {
  vector[J] observed_onrate = micro_conc * kon;
  vector[N] gp = gp_mu + L_cov * eta;
  vector[N] bg = preact_mean + preact_sd * gp;
  vector[N] mch_sub = mcherry_int - bg;
  vector[J] fold_change = (saturation + bg[timepoint_idx]) ./ bg[timepoint_idx];

}

model {
    vector[N] mu = saturation[idx] .* (1 - exp(-activation_time .* observed_onrate[idx]));
    vector[J] fc_mu = (1 + exp(-ep_ai)) ./ (1 + exp(-ep_ai) * (1 + power_density ./ theta_i) ./ (1 + power_density ./theta_a));

    // For GP
    eta ~ normal(0, 1);

    // For kinetics
    kon ~  normal(0, 100);
    saturation ~ normal(0, 1000);
    sigma ~ normal(0, 10);  
    mch_sub ~ normal(mu, sigma);

    // For fold-change
    ep_ai ~ normal(0, 10);
    theta_a ~ normal(0, 1);
    theta_i ~ normal(0, 1);
    fc_sigma ~ normal(0, 4);
    fold_change ~ normal(fc_mu, fc_sigma);
  }

