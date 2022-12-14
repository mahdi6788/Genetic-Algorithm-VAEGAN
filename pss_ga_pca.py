from google.colab import files
import numpy as np
from numpy.random import randint, rand
import pandas as pd
from scipy.signal import savgol_filter
from sklearn.model_selection import train_test_split, RepeatedKFold, cross_val_score, RandomizedSearchCV
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.decomposition import PCA
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
# %matplotlib inline

##### Plot #####
def plot_image(y,n):
  plt.figure(figsize=(20,1))
  plt.scatter(hnum[0],y)
  plt.plot(hnum[0],y)     
  plt.axis('off')
  plt.title(f"{n}")
  plt.show()

files.upload()

##### dataset_full including inputs and outputs #####
xy=pd.read_csv("dataset_full60.csv")
## Split into x,y ##
y=np.array([xy["efficiency"],xy["stress"],xy["deformation"]]).T
X=xy.drop(columns=["efficiency","stress","deformation"])
## float64 --> 32 ##
X=np.array(X,dtype="float32")
y=y.astype(np.float32)
## Scale the y ##
scaler= MinMaxScaler()
scaled_y= scaler.fit_transform(y)
Y=np.array(scaled_y)

### RandomForestRegressor ###
cv=RepeatedKFold(n_splits=5, n_repeats=10, random_state=2)
forest=RandomForestRegressor()
forest_cross=cross_val_score(forest,X,Y,scoring="neg_mean_squared_error", cv=cv, n_jobs=-1)
final_forest=forest.fit(X,Y)

# Upload x_dataset, y_dataset
files.upload()

##### dataset including only inputs (features) #####
v= pd.read_csv("y_dataset.csv")
h= pd.read_csv("x_dataset.csv")
vnum=v.to_numpy(dtype="float32")
hnum=h.to_numpy(dtype="float32")
## Split into train and test ##
train,test = train_test_split(vnum,test_size=0.2,random_state=42)

## PCA dataset ##
d=10
pca=PCA(n_components=d)
reduced=pca.fit_transform(train)

def pca_inverse(reduced):
  recovered= pca.inverse_transform(reduced)
  return recovered

##### Objective function #####
def predictions(decoded):
    pre=final_forest.predict(decoded)            
    ## Invert scaled to real data ##
    prediction=scaler.inverse_transform(pre) 
    return prediction

##### Decode function #####
def decode(individual):
    return pca_inverse(individual)

##### Fitness function #####
def fitness(p, efficiency_t):
  efficiency= predictions(decode(p))[0,0]
  fitness_score= (efficiency_t - efficiency) / efficiency_t
  return fitness_score

##### tournament (Selection) #####
def selection(pop,efficiency_t,k=5):
		# first random selection
		selection_ix = randint(len(pop))
		for ix in randint(0, len(pop), k-1):
				p1=np.array(pop[selection_ix]).reshape(1,-1)
				fitnessscore1=fitness(p1, efficiency_t)
				p2=np.array(pop[ix]).reshape(1,-1)
				fitnessscore2=fitness(p2, efficiency_t)
				# check if better (e.g. perform a tournament)
				if fitnessscore2 <= fitnessscore1:
						selection_ix = ix
		return pop[selection_ix]

##### Population function #####
## random dataset ##
def random(n_pop,codings_size):
  pop=[]
  noise=tf.random.normal(shape=[n_pop,codings_size])
  pop=np.array(noise)
  pop=pop.tolist()
  return pop

n_generations=60
n_pop=120
r_cross=0.8
r_mut=0.7
codings_size=10

efficiency_gen=[]
stress_gen=[]
deformation_gen=[]
## Initial population ##
pop= random(n_pop,codings_size)

for n in range(len(pop)):
  pp=np.array(pop[n]).reshape(1,-1)
  initialpop=pca_inverse(pp)
  initialpop=tf.reshape(initialpop,[200])
  m=predictions(decode(pp))
  plot_image(initialpop,n=m)
## keep track of the best solution ##
p=np.array(pop[0]).reshape(1,-1)
best= p
best_efficiency=predictions(decode(best))[0,0]
best_stress= predictions(decode(best))[0,1]
best_deformation= predictions(decode(best))[0,2]
## enumerate generations
for gen in range(n_generations):
  print("gen= ",gen)
  for i in range(n_pop):
    p=np.array(pop[i]).reshape(1,-1)
    decoded=decode(p)
    prediction= predictions(decoded)
    efficiency=prediction[0,0]
    stress=prediction[0,1]
    deformation=prediction[0,2]
## check for new best solution 
    if efficiency >= best_efficiency and stress <= best_stress or deformation <= best_deformation:
      best= p
      best_efficiency= efficiency
      best_stress= stress
      best_deformation= deformation
## select parents 
  parents=list()
  for n in range(n_pop):
    parents.append(selection(pop,0.77,k=5))
## create the next generation 
  children = list()
  for i in range(0, n_pop, 2):
    p1, p2 = parents[i], parents[i+1]
    c1, c2 = np.copy(p1), np.copy(p2)
    p1, p2=np.array(p1), np.array(p2)
    p1, p2=p1.tolist(), p2.tolist()
## Crossover and Mutation
    if rand() < r_cross:
      pt = randint(1, len(p1)-2)
      c1 = p1[:pt] + p2[pt:]
      c2 = p2[:pt] + p1[pt:]
    for c in [c1,c2]:
      c=np.array(c)
      for i in range(len(c)):
        if rand() < r_mut:
          c[i] = 1 - c[i]
      c=c.tolist()
      children.append(c)
## Replace population
  pop = children
  print(f"best{gen}= ",best,"\n" , f"best_prediction{gen}= ",[best_efficiency,best_stress,best_deformation])
  efficiency_gen.append(best_efficiency)
  stress_gen.append(best_stress)
  deformation_gen.append(best_deformation)
  y=pca_inverse(best)
  y=tf.reshape(y,[200])
  n=gen
  plot_image(y,n)

print(f"best{gen}= ",best,"\n" ,f"best_prediction{gen}= ",[best_efficiency,best_stress,best_deformation])
plot_image(y,n)

x_axis=np.arange(n_generations)
plt.figure(figsize=(5,5))
plt.plot(x_axis,efficiency_gen, label="Efficiency")
plt.legend()

plt.figure(figsize=(5,5))
plt.plot(x_axis,stress_gen, label="Stress")
plt.legend()

plt.figure(figsize=(5,5))
plt.plot(x_axis,deformation_gen, label="Deformation")
plt.legend()
