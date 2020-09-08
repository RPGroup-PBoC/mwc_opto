data {
    // Definition of the dimensional parameters
    int<lower=1> J; // Total number point identities
    int<lower=1> N_trace; //  Total number of trace measurements across points
    int<lower=1> N_preact; // Total number of preactivation measurements

    // Definition of the identity vectors
    int<lower=1, upper=J> point_idx[N_trace]; // Identification vector for point idenities


    // Define the observed data for the activation traces
    vector<lower=0>[N_trace] mch_trace; // Activation trace intensities
    vector<lower=0>[N_trace] relative_time_trace; // Time elapsed for each measurement from initiation of activation
    vector<lower=0>[N_trace] experiment_time_trace; // Time of the experiment in seconds.
    
    // Define the observed data for the preactivation intensities
    vector<lower=0>[N_preact] mch_preact; // Preactivation intensities
    vector<lower=0>[N_preact] experiment_time_preact; // Time of each preact intensity
}

transformed data {
    // Rescale preactivation intensities for gaussian processing
    vector[N_preact] mch_rescaled = (mch_preact - mean(mch_preact)) / sd(mch_preact);
    real delta = 1E-10; // Fudge factor for sampling

    // Generate a concatenation of the times to predict the laser fluctuation intensity
    real experiment_time_concat[N_preact];
    for (i in 1:N_preact) experiment_time_concat[i] = experiment_time_preact[i] / 60;
    // for (i in 1:N_preact) experiment_time_concat[N_preact + i] = experiment_time_preact[i] / 60;
}

parameters {
    // Define the parameters for the gaussian processing
    real<lower=0> rho;
    real<lower=0> alpha;
    vector[N_preact] eta;
    real<lower=0> gp_sigma; // Homoscedastic error for GP

    // Define parameters for kon estimation
    vector<lower=0>[J] a;
    vector<lower=0>[J] kon; 
    vector<lower=0>[J] trace_sigma;
    vector[J] sat;
}

transformed parameters { 
    // Generate a single vector containing the cholesky decomposition
    vector[N_preact] f;
    vector[N_preact] f_uncentered = sd(mch_preact) * f + mean(mch_preact);
    vector[N_trace] mch_trace_sub = mch_trace - f_uncentered[point_idx];
    // Define the mean and variance funcitons
    {
        // Define the param for the decomposition
        matrix[N_preact, N_preact] L_K;

        // Define the kernel as squared exponential
        matrix[N_preact, N_preact] K = cov_exp_quad(experiment_time_concat, alpha, rho);

        // Compute diagonas. 
        for (i in 1:N_preact) K[i, i] = K[i, i] + delta;
        L_K = cholesky_decompose(K);
        f = L_K * eta; // Add in stochastic noise
    }

}

model {
    // Compute the mean for the kinetic measurement
    vector[N_trace] mu;

    // Define the priors for the gaussian process
    rho ~ normal(0, 1000); 
    alpha ~ normal(0, 0.5);
    gp_sigma ~ normal(0, 0.1);
    eta ~ std_normal();

    // Define priors for kon inference    
    a ~ normal(0, 100);
    kon ~ normal(0, 100);
    trace_sigma ~ normal(0, 10);
    sat ~ normal(0, 1000);
    
    // Define likelihood for the gaussian process
    mch_rescaled ~ normal(f, gp_sigma);
    mu = a[point_idx] .* exp(-kon[point_idx] .* relative_time_trace) + sat[point_idx];
    mch_trace_sub ~ normal(mu, trace_sigma[point_idx]);

}

// generated quantities {
//     // Draw the predicted values from the gaussian process
//     vector[N_preact] preact_predicted_scaled;
//     vector[N_preact] preact_predicted;
//     for (i in 1:N_preact) preact_predicted_scaled[i] = normal_rng(f[i], gp_sigma);
//     preact_predicted = sd(mch_preact) * preact_predicted_scaled + mean(mch_preact);

// }
