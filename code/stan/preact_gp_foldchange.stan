data {
    int<lower=1> N; // Number of points observed
    int<lower=1> N_predict; // Number of points on which to predict
    vector[N] x; // Observed variate
    vector[N_predict] x_predict; // Predicted variate
    vector[N] y; // Covariate

    // Define the total mCherry intensity points. 
    vector[N] total_intensity;
}

transformed data {
    // Center and scale the variate and covariate data.
    vector[N] y_scaled = (y - mean(y)) / sd(y);
    real delta = 1E-10; // Fudge factor for sampling.

    // Concatenate the observed and prediction variates into a single vector. 
    int<lower=2> M = N + N_predict;
    real x_concat[M];
    for (i in 1:N) x_concat[i] = x[i] ;
    for (i in 1:N_predict) x_concat[N + i] = x_predict[i];
}

parameters {
    // Kernel parameters (squared exponential)
    real<lower=0> rho;
    real<lower=0> alpha;
    vector[M] eta; 

    // Homoscedastic measurement error
    real<lower=0> sigma;
}

transformed parameters {
    // Generate a single vector containing all cholesky decompositions. 
    vector[M] f;

    {
        matrix[M, M] L_K;
        matrix[M, M] K = cov_exp_quad(x_concat, alpha, rho);

        // Compute the diagonals
        for(i in 1:M) K[i, i] = K[i, i] + delta;

        // Compute the cholesky decomposition. 
        L_K = cholesky_decompose(K);
        f = L_K * eta; // Add in stochastic noise
    }

}

model {
    // Priors
    rho ~ inv_gamma(2, 2); 
    alpha ~ normal(0, 0.1);
    sigma ~ normal(0, 0.1);
    eta ~ std_normal();

    // Define the Gaussian process
    y_scaled ~ normal(f[1:N], sigma);
}


generated quantities {
    // Draw predicted values. 
    vector[N_predict] y_predict_scaled;
    vector [N_predict] y_predict;
    vector[N] fc_bg;
    vector[N] fc;
    for (i in 1:N) fc_bg[i] = normal_rng(f[i], sigma);
    for (i in 1:N_predict) y_predict_scaled[i] = normal_rng(f[N + i], sigma);

    // Compute the uncentering operations 
    y_predict = sd(y) * y_predict_scaled  + mean(y);

    // Compute the fold-change
    fc = total_intensity ./  fc_bg;
}