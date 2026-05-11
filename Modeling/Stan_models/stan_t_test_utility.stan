data {

  int<lower=1> Ns;
  int<lower=1> Nblocks;
  int<lower=1> maxTrials;
  int<lower=1> n_thetaz;
  int<lower=1> n_dthetaz;
  real v_thetaz[n_thetaz];
  real v_dthetaz[n_dthetaz];
  int<lower=1> subNtrials[Nblocks,Ns];
  int<lower=0,upper=1> g[Nblocks,maxTrials,Ns];
  int<lower=0,upper=1> c[Nblocks,maxTrials,Ns];
  int rg[Nblocks,maxTrials,Ns];
  int rs[Nblocks,maxTrials,Ns];
  int<lower=0,upper=1> self[Nblocks,maxTrials,Ns];
  real<lower=-1,upper=1> theta[Nblocks,maxTrials,Ns];
  real<lower=-1,upper=1> dtheta[Nblocks,maxTrials,Ns];
  int<lower=0,upper=1> acc[Nblocks,maxTrials,Ns];
  real noise[Ns];
  real noise_sd[Ns];
  real sigmas_mu[Ns];
  real sigmas_sd[Ns];
  real beta0_mu[Ns];
  real beta0_sd[Ns];
  real beta1_mu[Ns];
  real beta1_sd[Ns];
  real alpha_aa[Ns];
  real alpha_ab[Ns];
  real ppk_40[Ns];
  real ppk_80[Ns];
  real ppk_120[Ns];
  real powerL_mu[Ns];
  real powerL_sd[Ns];
  real powerG_mu[Ns];
  real powerG_sd[Ns];
  real averse_mu[Ns];
  real averse_sd[Ns];

  real mu_sigma_lb;
  real mu_sigma_ub;
  real sd_sigma_lb;
  real sd_sigma_ub;
  real mu_sigma_prior_mu;
  real mu_sigma_prior_sd;
  real y_lb;
  real y_ub;
  real mu_beta0_lb;
  real mu_beta0_ub;
  real sd_beta0_lb;
  real sd_beta0_ub;
  real mu_beta0_prior_mu;
  real mu_beta0_prior_sd;
  real mu_beta0_s_lb;
  real mu_beta0_s_ub;
  real mu_beta0_o_lb;
  real mu_beta0_o_ub;
  real mu_beta0_s_prior_mu;
  real mu_beta0_s_prior_sd;
  real mu_beta0_o_prior_mu;
  real mu_beta0_o_prior_sd;
  real mu_beta1_lb;
  real mu_beta1_ub;
  real sd_beta1_lb;
  real sd_beta1_ub;
  real mu_beta1_prior_mu;
  real mu_beta1_prior_sd;
  real mu_beta1_s_lb;
  real mu_beta1_s_ub;
  real mu_beta1_o_lb;
  real mu_beta1_o_ub;
  real mu_beta1_s_prior_mu;
  real mu_beta1_s_prior_sd;
  real mu_beta1_o_prior_mu;
  real mu_beta1_o_prior_sd;
  real mu_alpha_lb;
  real mu_alpha_ub;
  real sd_alpha_lb;
  real sd_alpha_ub;
  real mu_alpha_prior_mu;
  real mu_alpha_prior_sd;

  real mu_powerL_lb;
  real mu_powerL_ub;
  real sd_powerL_lb;
  real sd_powerL_ub;
  real mu_powerL_prior_mu;
  real mu_powerL_prior_sd;
  real mu_powerG_lb;
  real mu_powerG_ub;
  real sd_powerG_lb;
  real sd_powerG_ub;
  real mu_powerG_prior_mu;
  real mu_powerG_prior_sd;
  real mu_averse_lb;
  real mu_averse_ub;
  real sd_averse_lb;
  real sd_averse_ub;
  real mu_averse_prior_mu;
  real mu_averse_prior_sd;
}

parameters {

    real<lower=mu_alpha_lb,upper=mu_alpha_ub> mu_alpha;
    real<lower=sd_alpha_lb,upper=sd_alpha_ub> sd_alpha;
    real<lower=sd_beta0_lb,upper=sd_beta0_ub> sd_beta0;
    real<lower=mu_beta0_lb,upper=mu_beta0_ub> mu_beta0;
    real<lower=mu_beta1_lb,upper=mu_beta1_ub> mu_beta1;
    real<lower=sd_beta1_lb,upper=sd_beta1_ub> sd_beta1;

    real<lower=mu_powerL_lb,upper=mu_powerL_ub> mu_powerL;
    real<lower=sd_powerL_lb,upper=sd_powerL_ub> sd_powerL;
    real<lower=mu_powerG_lb,upper=mu_powerG_ub> mu_powerG;
    real<lower=sd_powerG_lb,upper=sd_powerG_ub> sd_powerG;
    real<lower=mu_averse_lb,upper=mu_averse_ub> mu_averse;
    real<lower=sd_averse_lb,upper=sd_averse_ub> sd_averse;

    row_vector<lower=mu_sigma_lb,upper=mu_sigma_ub>[Ns] sigma;
    row_vector<lower=mu_alpha_lb,upper=mu_alpha_ub>[Ns] alpha;
    row_vector<lower=mu_beta0_lb,upper=mu_beta0_ub>[Ns] beta0;
    row_vector<lower=mu_beta1_lb,upper=mu_beta1_ub>[Ns] beta1;
    row_vector<lower=-2,upper=2>[Ns] bds;

    row_vector<lower=mu_powerL_lb,upper=mu_powerL_ub>[Ns] powerL;
    row_vector<lower=mu_powerG_lb,upper=mu_powerG_ub>[Ns] powerG;
    row_vector<lower=mu_averse_lb,upper=mu_averse_ub>[Ns] averse;

    real<lower=y_lb,upper=y_ub> y[Nblocks,maxTrials,Ns];

}

transformed parameters {

  real aa;
	real ab;

	aa = mu_alpha * pow(sd_alpha,-2);
	ab = pow(sd_alpha,-2) - aa;

}
model {

  mu_alpha ~ normal(mu_alpha_prior_mu,mu_alpha_prior_sd);
  mu_beta0 ~ normal(mu_beta0_prior_mu,mu_beta0_prior_sd);
  mu_beta1 ~ normal(mu_beta1_prior_mu,mu_beta1_prior_sd);

  for (s in 1:Ns) {

        sigma[s] ~ normal(sigmas_mu[s],sigmas_sd[s]);
        bds[s] ~ normal(0.1, 0.001);
        alpha[s] ~ beta(alpha_aa[s],alpha_ab[s]);
        beta0[s] ~ normal(beta0_mu[s],beta0_sd[s]);
        beta1[s] ~ normal(beta1_mu[s],beta1_sd[s]);

        powerL[s] ~ normal(powerL_mu[s], powerL_sd[s]);
        powerG[s] ~ normal(powerG_mu[s], powerG_sd[s]);
        averse[s] ~ normal(averse_mu[s], averse_sd[s]);

        for (b in 1:Nblocks) {

        real k[maxTrials+1];
        real bd[maxTrials+1];

        k[1] = sigma[s];
        bd[1] = 0;

            for (i in 1:subNtrials[b,s]) {

                real EVr;
                real EVs;
                real PmCONDx_numerator[n_dthetaz];
                real PmCONDx_denomintor[n_dthetaz];
                real PMCONDx[n_dthetaz];
                real Pstate1CONDx_s;
                real Pstate2CONDx_s;
                real choice;
                real PcorCONDx_s;
                real PcorCONDm_o[n_dthetaz];
                real Ptemporary[n_dthetaz];
                real PcorCONDx_o;
                real pgamble;
                real p;
                real r;
                real d;
                real u;
                real term1;
                real term2;
                real term3;
                real gradient_v[n_dthetaz];
                real gradient;
                int min_diff_index;
                real difference[n_dthetaz];

                y[b,i,s] ~ normal(dtheta[b,i,s],sigma[s]);

                for (kk in 1:n_dthetaz) {
                    PmCONDx_numerator[kk]= exp(normal_lpdf(y[b,i,s]|v_dthetaz[kk],sigma[s]));
                }
                for (kk in 1:n_dthetaz) {
                    PmCONDx_denomintor[kk]= sum(PmCONDx_numerator);
                }
                for (kk in 1:n_dthetaz) {
                    PMCONDx[kk]= PmCONDx_numerator[kk]/PmCONDx_denomintor[kk];
                }

                Pstate1CONDx_s= sum(PMCONDx[1:n_thetaz])/sum(PMCONDx);
                Pstate2CONDx_s= sum(PMCONDx[n_thetaz+1:n_thetaz*2])/sum(PMCONDx);

                if (Pstate1CONDx_s > Pstate2CONDx_s) {
                  choice = 1;
                } else if (Pstate1CONDx_s < Pstate2CONDx_s) {
                  choice = 0;
                }

                if (choice == 1) {
                  PcorCONDx_s = Pstate1CONDx_s;
                } else if (choice == 0) {

                  PcorCONDx_s = Pstate2CONDx_s;
                }

                if (acc[b,i,s]==0) {
                  r = 0;
                } else if (acc[b,i,s]==1) {
                  r = 1;
                }

                if(r==1 && y[b,i,s]>bd[i]){
                  bd[i+1]=y[b,i,s];
                }else if (r==1 && bd[i]>y[b,i,s]){
                  bd[i+1]=bd[i];
                }else if (r==0 && bd[i]>y[b,i,s]){
                  bd[i+1]=y[b,i,s];
                }else if (r==0 && bd[i]<y[b,i,s]){
                  bd[i+1]=bd[i];
                }

                 for (kk in 1:n_dthetaz) {
                  if (v_dthetaz[kk]<0) {
                    PcorCONDm_o[kk]= normal_cdf(0,v_dthetaz[kk],k[i]);
                  } else if (v_dthetaz[kk]>0) {
                    PcorCONDm_o[kk]= normal_cdf(0,v_dthetaz[kk],k[i]);
                  }
                }
                for (kk in 1:n_dthetaz) {
                  Ptemporary[kk] = PMCONDx[kk] * PcorCONDm_o[kk];
                }
                PcorCONDx_o = sum(Ptemporary);

                if (PcorCONDx_s<.01) {
                    PcorCONDx_s=.01;
                } else if (PcorCONDx_s>.99) {
                    PcorCONDx_s=.99;
                } else if (PcorCONDx_o<.01) {
                    PcorCONDx_o=.01;
                } else if (PcorCONDx_o>.99) {
                    PcorCONDx_o=.99;
                }

                if (self[b,i,s] == 1) {
                  EVr = rg[b,i,s]*PcorCONDx_s - rg[b,i,s]*(1-PcorCONDx_s);
                } else if (self[b,i,s] == 0) {
                  EVr = PcorCONDx_o*(20^powerG[s]) - (1-PcorCONDx_o)*averse[s]*(20^powerL[s]);
				          EVs = PcorCONDx_s*(5^powerG[s]) - (1-PcorCONDx_s)*averse[s]*(5^powerL[s]);
                }

                if (self[b,i,s] == 1) {
                  pgamble = inv_logit(beta0[s] + beta1[s]*(EVr - EVs));
                } else if (self[b,i,s] == 0) {
                  pgamble = inv_logit(beta0[s] + beta1[s]*(EVr - EVs));
                }

                if (pgamble<.01) {
                    pgamble=.01;
                } else if (pgamble>.99) {
                    pgamble=.99;
                }

                if (self[b,i,s] == 1) {
                    c[b,i,s] ~  bernoulli_logit(100*(y[b,i,s]));
                }

                g[b,i,s] ~  bernoulli(pgamble);

                if (self[b,i,s] == 1) {
                  k[i+1] = k[i];
                } else if (self[b,i,s] == 0) {

                for (kk in 1:n_dthetaz) {
                  if (v_dthetaz[kk]<0) {
                    term1= v_dthetaz[kk]/k[i];
                    term2= PmCONDx_numerator[kk]/PmCONDx_denomintor[kk];
                    term3= exp(normal_lpdf(0|v_dthetaz[kk],k[i]));
                    gradient_v[kk]= term1*term2*term3;
                  } else if (v_dthetaz[kk]>0) {
                    term1= -v_dthetaz[kk]/(k[i]);
                    term2= PmCONDx_numerator[kk]/PmCONDx_denomintor[kk];
                    term3= exp(normal_lpdf(0|v_dthetaz[kk],(k[i])));
                    gradient_v[kk]= term1*term2*term3;
                  }
                }
                gradient= sum(gradient_v);

                p= PcorCONDx_o;
                if (acc[b,i,s]==0) {
                  r= 0;
                } else if (acc[b,i,s]==1) {
                  r= 1;
                }

                d= r-p;
                u= alpha[s]*d/gradient;
                k[i+1] = k[i]+u;

                  if (k[i+1]<.05) {
                      k[i+1]=.05;
                  }

                  if (k[i+1]>1) {
                      k[i+1]=1;
                  }

                  if (is_nan(k[i+1])==1) {
                      k[i+1]= k[i];
                  }

                }

            }
        }
  }
}

generated quantities {

  matrix[Ns,Nblocks*maxTrials] ppk;
  matrix[Ns,Nblocks*maxTrials] ppbd;
  matrix[Ns,Nblocks*maxTrials] ppx;
  matrix[Ns,Nblocks*maxTrials] ppCs;
  matrix[Ns,Nblocks*maxTrials] ppCo;
  matrix[Ns,Nblocks*maxTrials] ppEVr;
  matrix[Ns,Nblocks*maxTrials] ppPgamble;
  matrix[Ns,Nblocks*maxTrials] ppd;
  matrix[Ns,Nblocks*maxTrials] ppu;
  matrix[Ns,Nblocks*maxTrials] ppgradient;
  matrix[Ns,Nblocks*maxTrials] lik;
  real log_lik[Ns];

  vector[Ns] sigma_samples;
  vector[Ns] bds_samples;
  vector[Ns] alpha_samples;
  vector[Ns] beta0_samples;
  vector[Ns] beta1_samples;
  vector[3] initial_values;
  vector[Ns] powerL_samples;
  vector[Ns] powerG_samples;
  vector[Ns] averse_samples;

  for (s in 1:Ns) {

    int j;
    j = 1;

    log_lik[s] = 0;

    sigma_samples[s] = normal_rng(sigmas_mu[s],sigmas_sd[s]);
    bds_samples[s] = normal_rng(0.1, 0.001);
    alpha_samples[s] = beta_rng(alpha_aa[s],alpha_ab[s]);
    beta0_samples[s] = normal_rng(beta0_mu[s],beta0_sd[s]);
    beta1_samples[s] = normal_rng(beta1_mu[s],beta1_sd[s]);
    powerL_samples[s] = normal_rng(powerL_mu[s], powerL_sd[s]);
    powerG_samples[s] = normal_rng(powerG_mu[s], powerG_sd[s]);
    averse_samples[s] = normal_rng(averse_mu[s], averse_sd[s]);

    initial_values[1] = ppk_40[s];
    initial_values[2] = ppk_80[s];
    initial_values[3] = ppk_120[s];

    for (b in 1:Nblocks) {

        real k[maxTrials+1];
        real bd[maxTrials+1];

        if (b == 1) {
          k[1] = initial_values[1];
        } else if (b == 2) {
          k[1] = initial_values[2];
        } else if (b == 3) {
          k[1] = initial_values[3];
        } else {
          k[1] = sigma_samples[s];
        }

        bd[1] = bds_samples[s];

       for (i in 1:maxTrials) {

          if (i <= subNtrials[b,s]) {

                real EVr;
                real EVs;
                real PmCONDx_numerator[n_dthetaz];
                real PmCONDx_denomintor[n_dthetaz];
                real PMCONDx[n_dthetaz];
                real Pstate1CONDx_s;
                real Pstate2CONDx_s;
                real choice;
                real PcorCONDx_s;
                real PcorCONDm_o[n_dthetaz];
                real Ptemporary[n_dthetaz];
                real PcorCONDx_o;
                real pgamble;
                real p;
                real r;
                real d;
                real u;
                real x;
                real term1;
                real term2;
                real term3;
                real gradient_v[n_dthetaz];
                real gradient;
                int min_diff_index;
                real difference[n_dthetaz];

                x = y[b,i,s];
                ppx[s,j] = x;
                ppk[s,j] = k[i];
                ppbd[s,j] = bd[i];

                for (kk in 1:n_dthetaz) {
                    PmCONDx_numerator[kk]= exp(normal_lpdf(x|v_dthetaz[kk],sigma_samples[s]));
                }
                for (kk in 1:n_dthetaz) {
                    PmCONDx_denomintor[kk]= sum(PmCONDx_numerator);
                }
                for (kk in 1:n_dthetaz) {
                    PMCONDx[kk]= PmCONDx_numerator[kk]/PmCONDx_denomintor[kk];
                }

                Pstate1CONDx_s= sum(PMCONDx[1:n_thetaz])/sum(PMCONDx);
                Pstate2CONDx_s= sum(PMCONDx[n_thetaz+1:n_thetaz*2])/sum(PMCONDx);

                if (Pstate1CONDx_s > Pstate2CONDx_s) {
                  choice = 1;
                } else if (Pstate1CONDx_s < Pstate2CONDx_s) {
                  choice = 0;
                }

                if (choice == 1) {
                  PcorCONDx_s = Pstate1CONDx_s;
                } else if (choice == 0) {

                  PcorCONDx_s = Pstate1CONDx_s;
                }
                ppCs[s,j] = PcorCONDx_s;

                if (acc[b,i,s]==0) {
                  r = 0;
                } else if (acc[b,i,s]==1) {
                  r = 1;
                }

                if(r==1 && y[b,i,s]>bd[i]){
                  bd[i+1]=y[b,i,s];
                }else if (r==1 && bd[i]>y[b,i,s]){
                  bd[i+1]=bd[i];
                }else if (r==0 && bd[i]>y[b,i,s]){
                  bd[i+1]=y[b,i,s];
                }else if (r==0 && bd[i]<y[b,i,s]){
                  bd[i+1]=bd[i];
                }

                for (kk in 1:n_dthetaz) {
                  if (v_dthetaz[kk]<0) {
                    PcorCONDm_o[kk]= normal_cdf(0,v_dthetaz[kk],k[i]);
                  } else if (v_dthetaz[kk]>0) {
                    PcorCONDm_o[kk]= normal_cdf(0,v_dthetaz[kk],k[i]);
                  }
                }
                for (kk in 1:n_dthetaz) {
                  Ptemporary[kk] = PMCONDx[kk] * PcorCONDm_o[kk];
                }
                PcorCONDx_o = sum(Ptemporary);
                ppCo[s,j] = PcorCONDx_o;

                if (PcorCONDx_s<.01) {
                    PcorCONDx_s=.01;
                } else if (PcorCONDx_s>.99) {
                    PcorCONDx_s=.99;
                } else if (PcorCONDx_o<.01) {
                    PcorCONDx_o=.01;
                } else if (PcorCONDx_o>.99) {
                    PcorCONDx_o=.99;
                }

                if (self[b,i,s] == 1) {
                  EVr = rg[b,i,s]*PcorCONDx_s - rg[b,i,s]*(1-PcorCONDx_s);
                } else if (self[b,i,s] == 0) {
                  EVr = PcorCONDx_o*(20^powerG_samples[s]) - (1-PcorCONDx_o)*averse_samples[s]*(20^powerL_samples[s]);
				          EVs = PcorCONDx_s*(5^powerG_samples[s]) - (1-PcorCONDx_s)*averse_samples[s]*(5^powerL_samples[s]);
                }
                ppEVr[s,j] = EVr;

                if (self[b,i,s] == 1) {
                  pgamble = inv_logit(beta0_samples[s] + beta1_samples[s]*(EVr - EVs));
                } else if (self[b,i,s] == 0) {
                  pgamble = inv_logit(beta0_samples[s] + beta1_samples[s]*(EVr - EVs));
                }

                if (pgamble<.01) {
                    pgamble=.01;
                } else if (pgamble>.99) {
                    pgamble=.99;
                }
                ppPgamble[s,j] = pgamble;

                lik[s,j] = exp(bernoulli_lpmf(g[b,i,s]| pgamble));
                log_lik[s] = log_lik[s] + (bernoulli_lpmf(g[b,i,s]| pgamble));

                if (self[b,i,s] == 1) {
                    k[i+1] = k[i];
                    ppd[s,j] = 0;
                    ppu[s,j] = 0;
                } else if (self[b,i,s] == 0) {

                for (kk in 1:n_dthetaz) {
                  if (v_dthetaz[kk]<0) {
                    term1= v_dthetaz[kk]/k[i];
                    term2= PmCONDx_numerator[kk]/PmCONDx_denomintor[kk];
                    term3= exp(normal_lpdf(0|v_dthetaz[kk],k[i]));
                    gradient_v[kk]= term1*term2*term3;
                  } else if (v_dthetaz[kk]>0) {
                    term1= -v_dthetaz[kk]/(k[i]);
                    term2= PmCONDx_numerator[kk]/PmCONDx_denomintor[kk];
                    term3= exp(normal_lpdf(0|v_dthetaz[kk],k[i]));
                    gradient_v[kk]= term1*term2*term3;
                  }
                }
                gradient= sum(gradient_v);

                p= PcorCONDx_o;
                if (acc[b,i,s]==0) {
                  r= 0;
                } else if (acc[b,i,s]==1) {
                  r= 1;
                }

                d= r-p;
                u= alpha_samples[s]*d/gradient;
                k[i+1] = k[i]+u;
                ppd[s,j]= d;
                ppu[s,j]= u;
                ppgradient[s,j]= gradient;

                  if (k[i+1]<.05) {
                      k[i+1]=.05;
                  }

                  if (k[i+1]>1) {
                      k[i+1]=1;
                  }

                  if (is_nan(k[i+1])==1) {
                      k[i+1]= k[i];
                  }

                }

                j = j+1;

          } else {

                ppk[s,j] = 666;
                ppx[s,j] = 666;
                ppCs[s,j] = 666;
                ppCo[s,j] = 666;
                ppEVr[s,j] = 666;
                ppPgamble[s,j] = 666;
                ppd[s,j] = 666;
                ppu[s,j] = 666;
                ppgradient[s,j] = 666;
                lik[s,j] = 666;
                log_lik[s] = log_lik[s] + log(.5);
                j = j+1;

          }

      }
    }
  }

}
