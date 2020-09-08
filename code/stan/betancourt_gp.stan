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
  int<lower=1> N; // Number of observed measurements
  real x[N]; // Time points of observed measurements
  vector[N] y; //  Observed preactivation intensity

  int<lower=1> N_predict; // Number of desired time points over which to predict
  real x_predict[N_predict]; // Time points over which to predict
}

transformed data {
    vector[N] y_scaled = (y - mean(y)) ./ sd(y);
}

parameters {
  real<lower=0> rho;
  real<lower=0> alpha;
  real<lower=0> sigma;
}

model {
  matrix[N, N] cov =   cov_exp_quad(x, alpha, rho)
                     + diag_matrix(rep_vector(square(sigma), N));
  matrix[N, N] L_cov = cholesky_decompose(cov);

  rho ~ inv_gamma(2, 0.5);
  alpha ~ inv_gamma(0.01, 0.1);
  sigma ~ normal(0, 0.1);

  y_scaled ~ multi_normal_cholesky(rep_vector(0, N), L_cov);
}

generated quantities {
  vector[N_predict] f_predict = gp_pred_rng(x_predict, y_scaled, x, alpha, rho, sigma, 1e-10);
  vector[N_predict] y_predict_scaled;
  vector[N_predict] y_predict;
  for (i in 1:N_predict) y_predict_scaled[i] = normal_rng(f_predict[i], sigma);
  for (i in 1:N_predict) y_predict[i] = sd(y) * y_predict_scaled[i] + mean(y);
}

