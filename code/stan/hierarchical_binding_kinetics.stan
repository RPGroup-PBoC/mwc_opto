data { 
    // Dimensional parameters of data
    int<lower=1> J; // Number of unique power densities
    int<lower=1> M; // Number of unique traces 
    int<lower=1> N ;  // Total number of measurements
    int<lower=1, upper=J> power_idx[M]; // ID vector for powers
    int<lower=1, upper=M> point_idx[N]; // ID vector for points 

    // Specification of constants
    real<lower=0> micro_conc;  // Concentration of mCherry micro

    // Specification of observed data
    vector[N] mcherry_sub; // background subtracted mCherry 
    vector<lower=0>[N] relative_time; // Time dimension of binding

}

parameters {
    // Define the hyper parameters
    vector<lower=0>[J] kon_mu;  
    vector<lower=0>[J] kon_sigma; 
    vector<lower=0>[J] saturation_mu; 
    vector<lower=0>[J] saturation_sigma; 

    // Define low level priors
    vector<lower=0>[M] kon;
    vector<lower=0>[M] saturation;

    real<lower=0> sigma; // homoscedastic error    
}


model { 
    vector[N] mu = saturation[point_idx] .* (1 - exp(-relative_time .* kon[point_idx] * micro_conc));
    
    // Hyper prirors
    kon_mu ~ normal(0, 10);
    kon_sigma ~ normal(0, 1);
    saturation_mu ~ normal(0, 1000);
    saturation_sigma ~ normal(0, 1);

    // Low level priors
    kon ~ normal(kon_mu[power_idx], kon_sigma[power_idx]);
    saturation ~ normal(saturation_mu[power_idx], saturation_sigma[power_idx]);
    sigma ~ normal(0, 1);

    // Likelihood
    mcherry_sub ~ normal(mu, sigma);
}
