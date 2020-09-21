data { 
    // Dimensional parameters of data
    int<lower=1> J; // Number of unique traces
    int<lower=1> N ;  // Total number of measurements
    int<lower=1, upper=J> idx[N]; // ID vector for points 

    // Specification of constants
    real<lower=0> micro_conc;  // Concentration of mCherry micro

    // Specification of observed data
    vector[N] mcherry_sub; // background subtracted mCherry 
    vector<lower=0>[N] relative_time; // Time dimension of binding

}

parameters {
    vector<lower=0>[J] kon;  // on rate.
    vector<lower=0>[J] saturation; // Saturation level
    vector<lower=0>[J] sigma; // homoscedastic error    
}

transformed parameters {
    vector[J] observed_onrate = micro_conc * kon;
}

model { 
    vector[N] mu = saturation[idx] .* (1 - exp(-relative_time .* observed_onrate[idx]));
    kon ~ std_normal();
    saturation ~ normal(0, 100);
    sigma ~ normal(0, 10);
    mcherry_sub ~ normal(mu, sigma[idx]);
}
