

rm(list=ls())

script_path <- NA_character_
args <- commandArgs(trailingOnly = FALSE)
file_arg <- args[grepl("^--file=", args)]
if (length(file_arg) > 0) script_path <- normalizePath(sub("^--file=", "", file_arg[1]))
if (is.na(script_path)) script_path <- tryCatch(normalizePath(sys.frames()[[1]]$ofile), error = function(e) NA_character_)
if (!is.na(script_path) && nzchar(script_path)) {
  base_dir <- normalizePath(file.path(dirname(script_path), ".."))
} else {
  wd <- normalizePath(getwd())
  base_dir <- if (basename(wd) %in% c("Modeling", "Modelling")) normalizePath(file.path(wd, "..")) else wd
}
filesep <- .Platform$file.sep
require(R.matlab)
require(rstan)
require(parallel)

source(paste(base_dir,filesep,'Modeling',filesep,'Utils',filesep,'waic1.R',sep=""))
source(paste(base_dir,filesep,'Modeling',filesep,'Utils',filesep,'waic2.R',sep=""))

dir_fits <- paste(base_dir,filesep,'Modeling',filesep,'Stan_fits_27-3seeds_t',sep="")
dir_data <- paste(base_dir,filesep,'Data',sep="")
dir_stan <- paste(base_dir,filesep,'Modeling',sep="")
dir_modz <- paste(base_dir,filesep,'Modeling',filesep,'Stan_models',sep="")
dir_file <- paste(base_dir,filesep,'Modeling',filesep,'Files',sep="")
dir.create(dir_fits, showWarnings = FALSE, recursive = TRUE)

rstan_options(auto_write = TRUE)
options(mc.cores = parallel::detectCores())
auto_name_list <- function(...) {
  out <- list(...)
  expr <- as.list(substitute(list(...)))[-1]
  nms <- names(out)
  missing_names <- is.null(nms) || any(is.na(nms) | nms == "")
  if (missing_names) {
    if (is.null(nms)) nms <- rep("", length(out))
    unnamed <- is.na(nms) | nms == ""
    nms[unnamed] <- vapply(expr[unnamed], deparse, character(1), width.cutoff = 500)
    names(out) <- nms
  }
  out
}

models <- c('t_test')

subjects <- c('001_t','002_t','003_t','004_t','005_t','006_t','007_t','008_t','009_t','010_t','011_t','012_t','013_t','014_t','015_t','016_t','017_t','019_t','021_t','022_t','023_t','024_t','025_t','026_t','027_t','028_t','029_t')

Niter <- 8000
Nreruns <- 2
outsamp <- 500
seedz <- c('2','3')

y_lb <- -2
y_ub <- 2
mu_sigma_prior_mu <- .2
mu_sigma_prior_sd <- .2
mu_sigma_lb <- .05
mu_sigma_ub <- 2
sd_sigma_lb <- 0
sd_sigma_ub <- .5
mu_beta0_prior_mu <- 0
mu_beta0_prior_sd <- 10
mu_beta0_lb <- -10
mu_beta0_ub <- 10
sd_beta0_lb <- .01
sd_beta0_ub <- 10
mu_beta1_prior_mu <- .2
mu_beta1_prior_sd <- 2
mu_beta1_lb <- .01
mu_beta1_ub <- 2
sd_beta1_lb <- .01
sd_beta1_ub <- 2
mu_alpha_prior_mu <- .1
mu_alpha_prior_sd <- .1
mu_alpha_lb <- .0001
mu_alpha_ub <- 1
sd_alpha_lb <- 0
sd_alpha_ub <- 1
mu_factor_prior_mu <- 2
mu_factor_prior_sd <- 4
mu_factor_lb <- .01
mu_factor_ub <- 10
sd_factor_lb <- .01
sd_factor_ub <- 4
mu_beta0_s_prior_mu <- mu_beta0_prior_mu
mu_beta0_s_prior_sd <- mu_beta0_prior_sd
mu_beta0_s_lb <- mu_beta0_lb
mu_beta0_s_ub <- mu_beta0_ub
sd_beta0_s_lb <- sd_beta0_lb
sd_beta0_s_ub <- sd_beta0_ub
mu_beta0_o_prior_mu <- mu_beta0_prior_mu
mu_beta0_o_prior_sd <- mu_beta0_prior_sd
mu_beta0_o_lb <- mu_beta0_lb
mu_beta0_o_ub <- mu_beta0_ub
sd_beta0_o_lb <- sd_beta0_lb
sd_beta0_o_ub <- sd_beta0_ub
mu_beta1_s_prior_mu <- mu_beta1_prior_mu
mu_beta1_s_prior_sd <- mu_beta1_prior_sd
mu_beta1_s_lb <- mu_beta1_lb
mu_beta1_s_ub <- mu_beta1_ub
sd_beta1_s_lb <- sd_beta1_lb
sd_beta1_s_ub <- sd_beta1_ub
mu_beta1_o_prior_mu <- mu_beta1_prior_mu
mu_beta1_o_prior_sd <- mu_beta1_prior_sd
mu_beta1_o_lb <- mu_beta1_lb
mu_beta1_o_ub <- mu_beta1_ub
sd_beta1_o_lb <- sd_beta1_lb
sd_beta1_o_ub <- sd_beta1_ub

Ntrials <- 40
Nblocks <- 3
Nsubjects <- length(subjects)

g_matrix <- array(0, c(Nblocks, Ntrials, length(subjects)))
c_matrix <- array(0, c(Nblocks, Ntrials, length(subjects)))
d_matrix <- array(0, c(Nblocks, Ntrials, length(subjects)))
rg_matrix <- array(0, c(Nblocks, Ntrials, length(subjects)))
rs_matrix <- array(0, c(Nblocks, Ntrials, length(subjects)))
self_matrix <- array(0, c(Nblocks, Ntrials, length(subjects)))
acc_matrix <- array(0, c(Nblocks, Ntrials, length(subjects)))
theta_matrix <- array(0, c(Nblocks, Ntrials, length(subjects)))
dtheta_matrix <- array(0, c(Nblocks, Ntrials, length(subjects)))
subNtrials <- array(0, c(Nblocks, length(subjects)))
sigma_mu_vector <- array(0, length(subjects))
sigma_sd_vector <- array(0, length(subjects))

sigmas_mu_vector <- array(0, length(subjects))
sigmas_sd_vector <- array(0, length(subjects))
beta0_mu_vector <- array(0, length(subjects))
beta0_sd_vector <- array(0, length(subjects))
beta1_mu_vector <- array(0, length(subjects))
beta1_sd_vector <- array(0, length(subjects))
alpha_aa_vector <- array(0, length(subjects))
alpha_ab_vector <- array(0, length(subjects))
ppk_40_vector <- array(0, length(subjects))
ppk_80_vector <- array(0, length(subjects))
ppk_120_vector <- array(0, length(subjects))

for (subi in 1:Nsubjects){
  
  setwd(dir_file)
  TMP <- readMat('noise.mat')
  sigma_mu_vector[subi] <- TMP$sigma.mu[subi]
  sigma_sd_vector[subi] <- TMP$sigma.sd[subi]

  setwd(dir_file)
  SIGMA <- readMat('sigma.mat')
  sigmas_mu_vector[subi] <- SIGMA$sigmas.mu[subi]
  sigmas_sd_vector[subi] <- SIGMA$sigmas.sd[subi]

  setwd(dir_file)
  BETA0 <- readMat('beta0.mat')
  beta0_mu_vector[subi] <- BETA0$beta0.mu[subi]
  beta0_sd_vector[subi] <- BETA0$beta0.sd[subi]

  setwd(dir_file)
  BETA1 <- readMat('beta1.mat')
  beta1_mu_vector[subi] <- BETA1$beta1.mu[subi]
  beta1_sd_vector[subi] <- BETA1$beta1.sd[subi]

  setwd(dir_file)
  ALPHA <- readMat('alpha.mat')
  alpha_aa_vector[subi] <- ALPHA$alpha.aa[subi]
  alpha_ab_vector[subi] <- ALPHA$alpha.ab[subi]

  setwd(dir_file)
  PPK <- readMat('ppk.mat')
  ppk_40_vector[subi] <- PPK$ppk.40[subi]
  ppk_80_vector[subi] <- PPK$ppk.80[subi]
  ppk_120_vector[subi] <- PPK$ppk.120[subi]

  
  setwd(dir_data)
  DATA = readMat(paste('mriData_sub_',subjects[subi],'.mat',sep=""))
  dat = DATA$DATA
  
  k = array(0, c(Nblocks, Ntrials))
  theta = array(0, c(Nblocks, Ntrials))
  dtheta = array(0, c(Nblocks, Ntrials))
  self = array(0, c(Nblocks, Ntrials))
  rs = array(0, c(Nblocks, Ntrials))
  rg = array(0, c(Nblocks, Ntrials))
  acc = array(0, c(Nblocks, Ntrials))
  resp = array(0, c(Nblocks, Ntrials))
  gamble = array(0, c(Nblocks, Ntrials))
  err = array(0, c(Nblocks, Ntrials))
  
  for (b in 1:Nblocks) {
    
    trialInd = dimnames(dat[,,b]$trials)[[1]]
    typeIind = dimnames(dat[,,b]$typeI)[[1]]
    typeIIind = dimnames(dat[,,b]$typeII)[[1]]
    
    ind = which(match(trialInd, "d")==1)
    k[b,] = dat[,,b]$trials[[ind]]
    ind = which(match(trialInd, "theta")==1)
    theta[b,] = dat[,,b]$trials[[ind]]
    ind = which(match(trialInd, "self")==1)
    self[b,] = dat[,,b]$trials[[ind]]
    ind = which(match(trialInd, "rs")==1)
    rs[b,] = dat[,,b]$trials[[ind]]
    ind = which(match(trialInd, "rg")==1)
    rg[b,] = dat[,,b]$trials[[ind]]
    ind = which(match(typeIind, "response")==1)
    resp[b,] = dat[,,b]$typeI[[ind]]
    ind = which(match(typeIind, "correct")==1)
    acc[b,] = dat[,,b]$typeI[[ind]]
    ind = which(match(typeIIind, "response")==1)
    gamble[b,] = dat[,,b]$typeII[[ind]]
    dtheta[b,] = k[b,]*theta[b,]
    
    err[b,] = 0
    subNtrials[b,subi] <- sum(!err[b,])
    
    d_matrix[b,1:subNtrials[b,subi],subi] <- k[b,!err[b,]]
    c_matrix[b,1:subNtrials[b,subi],subi] <- resp[b,!err[b,]]-1
    g_matrix[b,1:subNtrials[b,subi],subi] <- gamble[b,!err[b,]]
    rg_matrix[b,1:subNtrials[b,subi],subi] <- rg[b,!err[b,]]
    rs_matrix[b,1:subNtrials[b,subi],subi] <- rs[b,!err[b,]]
    self_matrix[b,1:subNtrials[b,subi],subi] <- self[b,!err[b,]]
    acc_matrix[b,1:subNtrials[b,subi],subi] <- acc[b,!err[b,]]
    theta_matrix[b,1:subNtrials[b,subi],subi] <- theta[b,!err[b,]]
    dtheta_matrix[b,1:subNtrials[b,subi],subi] <- dtheta[b,!err[b,]]
    
    for (i in 1:40)
      if (self_matrix[b,i,subi]==0) {
        c_matrix[b,i,subi]= sample(0:1,1)
      }
    
  }
}

for (m in 1:length(models)) {
  
  setwd(dir_file)
  thetaz <- readMat('thetaz_2.mat')
  v_thetaz <- thetaz$v.thetaz.comp.linear[1,]
  v_dthetaz <- thetaz$v.dthetaz.comp.linear[1,]
  n_thetaz <- length(v_thetaz)
  n_dthetaz <- length(v_dthetaz)
  n_thetaz_real <- length(v_thetaz)
  n_dthetaz_real <- length(v_dthetaz)
  spaceSizeFull <- n_thetaz;
  spaceSizeFullN <- n_thetaz;
  spaceSizeFullSignedN <- spaceSizeFullN*2;
  spaceMin <- .001;
  spaceMax <- 3;
  
  setwd(dir_stan)
  data <- auto_name_list(Nblocks=Nblocks, maxTrials=Ntrials, Ns=Nsubjects, subNtrials=subNtrials,
               g=g_matrix, c=c_matrix, theta=theta_matrix, dtheta=dtheta_matrix, acc=acc_matrix, rg=rg_matrix, rs=rs_matrix, self=self_matrix,
               noise=sigma_mu_vector, noise_sd=sigma_sd_vector, sigmas_mu = sigmas_mu_vector, sigmas_sd = sigmas_sd_vector,
               beta0_mu=beta0_mu_vector, beta0_sd=beta0_sd_vector, beta1_mu=beta1_mu_vector, beta1_sd=beta1_sd_vector,
               alpha_aa=alpha_aa_vector, alpha_ab=alpha_ab_vector, ppk_40=ppk_40_vector, ppk_80=ppk_80_vector, ppk_120=ppk_120_vector,
               n_thetaz, n_dthetaz, n_thetaz_real, n_dthetaz_real, v_thetaz, v_dthetaz,
               spaceSizeFull, spaceSizeFullN, spaceSizeFullSignedN, spaceMin, spaceMax,
               y_lb, y_ub,
               mu_sigma_lb, mu_sigma_ub, sd_sigma_lb, sd_sigma_ub, mu_sigma_prior_mu, mu_sigma_prior_sd,
               mu_beta0_prior_mu, mu_beta0_prior_sd, mu_beta0_lb, mu_beta0_ub, sd_beta0_lb, sd_beta0_ub,
               mu_beta0_s_prior_mu, mu_beta0_s_prior_sd, mu_beta0_s_lb, mu_beta0_s_ub, sd_beta0_s_lb, sd_beta0_s_ub,
               mu_beta0_o_prior_mu, mu_beta0_o_prior_sd, mu_beta0_o_lb, mu_beta0_o_ub, sd_beta0_o_lb, sd_beta0_o_ub,
               mu_beta1_prior_mu, mu_beta1_prior_sd, mu_beta1_lb, mu_beta1_ub, sd_beta1_lb, sd_beta1_ub,
               mu_beta1_s_prior_mu, mu_beta1_s_prior_sd, mu_beta1_s_lb, mu_beta1_s_ub, sd_beta1_s_lb, sd_beta1_s_ub,
               mu_beta1_o_prior_mu, mu_beta1_o_prior_sd, mu_beta1_o_lb, mu_beta1_o_ub, sd_beta1_o_lb, sd_beta1_o_ub,
               mu_alpha_prior_mu, mu_alpha_prior_sd, mu_alpha_lb, mu_alpha_ub, sd_alpha_lb, sd_alpha_ub,
               mu_factor_prior_mu, mu_factor_prior_sd, mu_factor_lb, mu_factor_ub, sd_factor_lb, sd_factor_ub)
  
  
  for (iter in 1:Nreruns) {
    
    seed <- sample(1:10000,1)
      parameters <- c('sigma','mu_beta0','beta0','mu_beta1','beta1','mu_alpha','alpha','ppk','ppx','ppCs','ppCo','ppEVr','ppPgamble','ppd','ppu','lik','log_lik','sigma_samples','beta0_samples','beta1_samples','alpha_samples')
      group_param <- c('mu_beta0','mu_beta1','mu_alpha')
      subject_param <- c('sigma','beta0','beta1','alpha')

    
    filz <- stan_model(file = paste(dir_modz,filesep,'stan_',models[m],'.stan',sep=""))
    
    fitz <- vb(filz, data = data, pars = parameters, include = TRUE,
               seed = seed, iter=Niter, elbo_samples=200, eval_elbo=100, output_samples=outsamp, tol_rel_obj=.0001)
    
    samp = extract(fitz)
    
    evlz = waic1(fitz)
    groupWAIC <- evlz$waic
    groupLOO <- -2*evlz$elpdLoo
    subjectWAIC <- NULL
    subjectLOO <- NULL
    

    
    for (i in 1:length(subjects)) {
      lik <- (samp$lik[,i,])
      lik <- t(lik)
      keep <- lik[,1] < 1
      lik <- lik[keep,]
      log_lik <- log(lik)
      log_lik <- t(log_lik)
      evlz <- waic2(log_lik)
      subjectWAIC[i] <- evlz$waic
      subjectLOO[i] <- -2*evlz$elpdLoo
    }
    
    group_param_MAP <- NULL
    group_param_upper_CI <- NULL
    group_param_lower_CI <- NULL
    q95 <- c(0.025,0.975)
    for (i in 1:length(group_param)){
      sample_vector = as.numeric(samp[group_param[i]][[1]])
      group_param_MAP[group_param[i]] <- density(sample_vector)$x[which(density(sample_vector)$y ==
                                                                          max(density(sample_vector)$y))]
      group_param_upper_CI[group_param[i]] <- quantile(sample_vector,probs=q95[2])
      group_param_lower_CI[group_param[i]] <- quantile(sample_vector,probs=q95[1])
    }
    
    subject_param <- NULL
    subject_predict <- NULL
      subject_param$sigma <- colMeans(samp$sigma)
      subject_param$beta0 <- colMeans(samp$beta0)
      subject_param$beta1 <- colMeans(samp$beta1)
      subject_param$alpha <- colMeans(samp$alpha)
      
      subject_param$sigma_sd <- apply(samp$sigma, 2, sd, na.rm = TRUE)
      subject_param$beta0_sd <- apply(samp$beta0, 2, sd, na.rm = TRUE)
      subject_param$beta1_sd <- apply(samp$beta1, 2, sd, na.rm = TRUE)
      subject_param$alpha_sd <- apply(samp$alpha, 2, sd, na.rm = TRUE)
      
      subject_predict$ppk <- apply(samp$ppk, c(2,3), mean)
      subject_predict$ppx <- apply(samp$ppx, c(2,3), mean)
      subject_predict$ppCs <- apply(samp$ppCs, c(2,3), mean)
      subject_predict$ppCo <- apply(samp$ppCo, c(2,3), mean)
      subject_predict$ppEVr <- apply(samp$ppEVr, c(2,3), mean)
      subject_predict$ppPgamble <- apply(samp$ppPgamble, c(2,3), mean)
      subject_predict$ppd <- apply(samp$ppd, c(2,3), mean)
      subject_predict$ppu <- apply(samp$ppu, c(2,3), mean)
      subject_predict$lik <- apply(samp$lik, c(2,3), mean)
      
      subject_param$aa <- subject_param$alpha * (1 / subject_param$alpha_sd^2)
      subject_param$ab <- 1 / subject_param$alpha_sd^2 - subject_param$aa
      ppPgamble <- (samp$ppPgamble)

    
    
    writeMat(file.path(dir_fits, paste('model_',models[m],'_seed_',seedz[iter],'_vb.mat',sep="")),
             group_param_names=group_param, group_param_MAP=group_param_MAP, group_param_upper_CI=group_param_upper_CI, group_param_lower_CI=group_param_lower_CI,
             subject_param=subject_param,subject_predict=subject_predict, ppPgamble = ppPgamble,
             groupWAIC=groupWAIC, subjectWAIC=subjectWAIC, groupLOO=groupLOO, subjectLOO=subjectLOO, seed=seed)
    
  }
  
}


