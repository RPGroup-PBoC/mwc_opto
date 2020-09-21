data { 
    int<lower=1> N; // number of fold-change measurements
    vector<lower=0>[N] rho;
    vector[N] foldchange;
}

parameters { 
    real<lower=0> theta_a;
    real<lower=0> theta_i;
    real ep_ai;
    real<lower=0> sigma;
}

model {
    vector[N] mu = (1 + exp(-ep_ai)) ./ (1 + exp(-ep_ai) * (1 + rho/theta_a) ./ (1 + rho/theta_i));
    
    theta_a ~ std_normal();
    theta_i ~ std_normal();
    ep_ai ~ normal(-5, 3);
    sigma ~ std_normal();
    
    foldchange ~ cauchy(mu, sigma);
}