# Imports from supporting functions
from reg_functions import *
from support_funcs import *

# Import of relevant packages
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.model_selection import train_test_split

#Default for plots
plt.rcParams["figure.figsize"] = (15,7)

# Random seed
np.random.seed(2018)

# Case selection (Data function, y)
case_s = ['1d', '2d', 'Franke']
case = case_s[0]

# Grid and data setup
a, b   = 1.0, 1.5                            # Coefficients for exponential model
c0, c1 = 0.01, 0.5                           # Noise scaling    
x0, xN = 0, 1                                # Start and end of domain, x-axis
y0, yN = 0, 0.8                                # Start and end of domain, y-axis
Nx, Ny = 100, 100                            # Number of sample points

x   = np.sort(np.random.uniform(x0,xN,Nx)).reshape(-1,1) # Mesh points on x-axis (uniformly distributed, sorted values)
y   = np.sort(np.random.uniform(y0,yN,Ny)).reshape(-1,1) # Mesh points on y-axis (uniformly distributed, sorted values) (try different length arrays in x and y if singular values are an issue)
x_n = np.random.normal(0, c0, x.shape)                    # Noise for x-axis
y_n = np.random.normal(0, c0, y.shape)                    # Noise for y-axis

# Data model selection
if case == '1d':
    z_data = exp1D(x,x_n,a=a,b=b,noise=c1)
elif case == '2d':
    z_data = exp2D(x,y,x_n,y_n,a=a,b=b,noise=c1)
elif case == 'Franke':
    z_data = Franke(x,y,x_n,y_n,noise=c1)

fig,ax = plt.subplots(1,1)
ax.scatter(x,z_data)

## Polynomial degree setup
maxdegree   = 5
poly_deg    = np.arange(1,maxdegree+1,1)

# Training and test data ratio
train_split = 4/5
test_split  = 1.0 - train_split 
train_l     = int(np.round(len(x)*train_split))
test_l      = int(np.round(len(x)*test_split))

## Dictionaries for storing values from regression analysis
mod_train, mod_test = {},{}
intcept, betas  = {},{}
mse_s, r2_s     = {},{}

## OLS-regression
# Loop storage for output values from regression
mod_tr_ols, mod_ts_ols = {},{}
itcpt_ols,btas_ols = {},{}
mse_ols,r2_ols     = {},{}

# Storing intercept values for OLS-analysis for using in Ridge and Lasso-analysis
beta_0 = np.zeros(maxdegree)

# Data set split
if case == '1d':
    x_train,x_test,z_train,z_test = train_test_split(x,z_data,test_size=test_split)
    x_data = [x_train,x_test]; z_data = [z_train,z_test]
else:
    x_train,x_test,y_train,y_test,z_train,z_test = train_test_split(x,y,z_data,test_size=test_split)
    x_data = [x_train,x_test,y_train,y_test]; z_data = [z_train,z_test]

# OLS loop
for i, p_d in enumerate(poly_deg):

    #y_train_tmp,y_test_tmp,intcept_tmp,beta_tmp,mse_s_tmp,r2_s_tmp = RegOLS_skl(y_data=z_data,x_data=x_data,polydeg=p_d)
    y_train_tmp,y_test_tmp,intcept_tmp,beta_tmp,mse_s_tmp,r2_s_tmp = RegOLS(y_data=z_data,x_data=x_data,polydeg=p_d)


    mod_tr_ols['train_p_'+str(p_d)] = y_train_tmp; mod_ts_ols['test_p_'+str(p_d)] = y_test_tmp
    itcpt_ols['p_'+str(p_d)] = intcept_tmp; btas_ols['beta_p_'+str(p_d)] = beta_tmp
    mse_ols['p_'+str(p_d)] = mse_s_tmp; r2_ols['p_'+str(p_d)] = r2_s_tmp 

    beta_0[i] = intcept_tmp

mod_train['y_tr_ols'] = mod_tr_ols; mod_test['y_ts_ols'] = mod_ts_ols; 
intcept['intercept_ols'] = itcpt_ols; betas['betas_ols'] = btas_ols
mse_s['mse_ols'] = mse_ols; r2_s['r2_ols'] = r2_ols

#lmbda = np.logspace(-10,2,10)
lmbda = [1e-5,1e-4,1e-3,1e-2,1e-1,1e0]
## Ridge-regression
# Loop storage for output values from regression
y_tr_ridge, y_ts_ridge = {},{}
itcpt_ridge,btas_ridge = {},{}
mse_ridge,r2_ridge     = {},{}

# Ridge loop
for i, p_d in enumerate(poly_deg):

    y_train_tmp,y_test_tmp,intcept_tmp,beta_tmp,mse_s_tmp,r2_s_tmp = RegRidge(y_data=z_data,x_data=x_data,polydeg=p_d,
                                                                        lmbda=lmbda, intcept=beta_0[i], scale=True)#, prnt=True)

    y_tr_ridge['train_p_'+str(p_d)] = y_train_tmp; y_ts_ridge['test_p_'+str(p_d)] = y_test_tmp
    itcpt_ridge['p_'+str(p_d)] = intcept_tmp; btas_ridge['beta_p_'+str(p_d)] = beta_tmp
    mse_ridge['p_'+str(p_d)] = mse_s_tmp; r2_ridge['p_'+str(p_d)] = r2_s_tmp 

mod_train['y_tr_ridge'] = y_tr_ridge; mod_test['y_ts_ridge'] = y_ts_ridge; 
intcept['intercept_ridge'] = itcpt_ridge; betas['betas_ridge'] = btas_ridge
mse_s['mse_ridge'] = mse_ridge; r2_s['r2_ridge'] = r2_ridge

## Lasso Regression
# Loop storage for output values from regression
y_tr_lasso, y_ts_lasso = {},{}
itcpt_lasso,btas_lasso = {},{}
mse_lasso,r2_lasso     = {},{}

# Lasso loop
for i, p_d in enumerate(poly_deg):

    y_train_tmp,y_test_tmp,intcept_tmp,beta_tmp,mse_s_tmp,r2_s_tmp = RegLasso(y_data=z_data,x_data=x_data, polydeg=p_d,
                                                                        lmbda=lmbda, intcept=beta_0[i], maxit=10000)#, scale=False)#, prnt=True)
    
    y_tr_lasso['train_p_'+str(p_d)] = y_train_tmp; y_ts_lasso['test_p_'+str(p_d)] = y_test_tmp
    itcpt_lasso['p_'+str(p_d)] = intcept_tmp; btas_lasso['beta_p_'+str(p_d)] = beta_tmp
    mse_lasso['p_'+str(p_d)] = mse_s_tmp; r2_lasso['p_'+str(p_d)] = r2_s_tmp 

mod_train['y_tr_lasso'] = y_tr_lasso; mod_test['y_ts_lasso'] = y_ts_lasso; 
intcept['intercept_lasso'] = itcpt_lasso; betas['betas_lasso'] = btas_lasso
mse_s['mse_lasso'] = mse_lasso; r2_s['r2_lasso'] = r2_lasso

## Plotting results
# Packing up metrics for plotting
plot_heatmap(x_data=poly_deg,y_data=lmbda,values=mse_s['mse_ridge'],labels=['Ridge','MSE','poly.deg','λ','Training','Test'])
plot_heatmap(x_data=poly_deg,y_data=lmbda,values=r2_s['r2_ridge'],labels=['Ridge','R²','poly.deg','λ','Training','Test'])
#plot_OLS(poly_deg,y_data=[mse_s['mse_ols'],r2_s['r2_ols']],labels=['OLS','poly.deg','MSE','R²'])
#beta_plot(poly_deg,betas_ols,x_label='poly. degree',y_label=r'$\hat{\beta}$')
#plot_reg1D(x_data=x,y_data=z_data,b_data=betas_ols,b0=intcept_ols,labels=['OLS','x',r'$\tilde{y}$(x)'])

## Plotting results for Ridge-regression 
#plot_RiLa(poly_deg,y_data=[mse_s['mse_ridge'],r2_s['r2_ridge']],labels=['Ridge','poly.deg','MSE','R²'],lmbda=lmbda)
#plot_RiLa(poly_deg,y_data=[mse_s['mse_lasso'],r2_s['r2_lasso']],labels=['Lasso','poly.deg','MSE','R²'],lmbda=lmbda)

#plot_compare(x_data=poly_deg,y_data=[mse_s,r2_s],labels=['','poly.deg','MSE','R²'])

#plot_reg1D(x_data=x,y_data=z_data,b_data=betas_ols,b0=intcept_ols,labels=['OLS','x',r'$\tilde{y}$(x)'])

plt.show()
#"""
