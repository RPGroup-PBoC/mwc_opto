functions {
  vector gp_pred_rng(real[] x2,
                     vector y1, real[] x1,
                     real alpha, real rho, real sigma, real delta) {
    int N1 = rows(y1);
    int N2 = size(x2);
    vector[N2] f2;
    {
      matrix[N1, N1] K =   cov_exp_quad(x1, alpha, rho)
                         + diag_matrix(rep_vector(square(sigma), N1));
      matrix[N1, N1] L_K = cholesky_decompose(K);

      vector[N1] L_K_div_y1 = mdivide_left_tri_low(L_K, y1);
      vector[N1] K_div_y1 = mdivide_right_tri_low(L_K_div_y1', L_K)';
      matrix[N1, N2] k_x1_x2 = cov_exp_quad(x1, x2, alpha, rho);
      vector[N2] f2_mu = (k_x1_x2' * K_div_y1);
      matrix[N1, N2] v_pred = mdivide_left_tri_low(L_K, k_x1_x2);
      matrix[N2, N2] cov_f2 =   cov_exp_quad(x2, alpha, rho) - v_pred' * v_pred
                              + diag_matrix(rep_vector(delta, N2));
      f2 = multi_normal_rng(f2_mu, cov_f2);
    }
    return f2;
  }
}

data {
    // Dimensional parameters  
    int<lower=1> J; // Number of unique time traces>
    int<lower=1> N; // Number of light-activated measurements
    int<lower=1> M; // Number of preactivation intensity measures.

    // Identification vectors
    int<lower=1, upper=J> idx[N]; // ID vector for individual traces

    // Preactivation intensity data for GP background subtraction
    vector<lower=0>[M] preact_int;  // Preactivation mCherry intensity
    real<lower=0> preact_time[M]; // Experiment time of measurements
    
    // Kinetics data 
    vector[N] mcherry_int; // Observed mCherry intensity 
    real<lower=0> experiment_time[N]; // Time of experiment for gp subtraction
    vector<lower=0>[N] activation_time; // Relative time for activation
    real<lower=0> micro_conc; // Concentration of micro


    
    // GP hyperparameters
    real alpha_mean;
    real rho_mean;
    real sigma_mean;
}

transformed data {
    // Scale the covariate to be closer to unity
    vector[M] preact_scaled = (preact_int - mean(preact_int)) ./ sd(preact_int);

    // Compute the expected background intensity from wandering laser.
    vector[N] f_predict = gp_pred_rng(experiment_time, preact_scaled, preact_time,
                                     alpha_mean, rho_mean, sigma_mean, 1e-10);
    vector[N] bg_predict_scaled;
    vector[N] bg_predict;
    vector[N] mcherry_sub;
    for (i in 1:N) bg_predict_scaled[i] = normal_rng(f_predict[i], sigma_mean);
    for (i in 1:N) bg_predict[i] = sd(preact_int) * bg_predict_scaled[i] + mean(preact_int);

    // Do the background subtraction
    mcherry_sub = mcherry_int - bg_predict;
}

parameters {
  // Kinetic Parameters
  vector<lower=0>[J] kon;
  vector<lower=0>[J] saturation;
  real<lower=0> sigma;
}

transformed parameters {
  vector[J] observed_onrate = micro_conc * kon;
}

model {
    vector[N] mu;
    for (i in 1:N) mu[i] = saturation[idx[i]] .* (1 - exp(-activation_time[i] .* observed_onrate[idx[i]]));
    kon ~  inv_gamma(1.5, 1.5);
    saturation ~ normal(0, 1000);
    sigma ~ normal(0, 10);
    mcherry_sub ~ normal(mu, sigma);
    }

generated quantities { 

}

  