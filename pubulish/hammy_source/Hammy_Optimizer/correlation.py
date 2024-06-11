import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns





def make_correlation_matrix(df, save_path):

    cor = df.corr(method='spearman')
    print(cor)  
    plt.figure(figsize=(25, 25))

    plt.style.use('seaborn-whitegrid')
    sns.set_style('white')
    ax =sns.heatmap(cor,
                    annot=True,  
                    center= 0,  
                    fmt='.2f', 
                    linewidth= 1,  
                    linecolor='white',  
                    vmax= 1, vmin=-1,
                    xticklabels=True, yticklabels=True,  
                    square=True,  
                    cbar=True,  
                    cbar_kws={"shrink": 0.8},
                    cmap='vlag',  
                    annot_kws={"fontsize":12}
                    )    
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=12)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20) 
    plt.savefig(save_path, dpi=300)  
    plt.ion()  
    plt.close('all')  