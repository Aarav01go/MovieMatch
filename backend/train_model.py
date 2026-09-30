import pandas as pd
from surprise import Dataset, Reader, SVD, KNNBaseline, BaselineOnly
import pickle
import os

def train_and_save_model():
    print("Loading data...")
    ratings = pd.read_csv('ratings.csv')
    
    reader = Reader(rating_scale=(0.5, 5.0))
    data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)
    
    print("Building full trainset...")
    trainset = data.build_full_trainset()
    
    models = {
        'svd': SVD(),
        'knn': KNNBaseline(sim_options={'name': 'pearson_baseline', 'user_based': False}),
        'baseline': BaselineOnly()
    }
    
    for name, algo in models.items():
        print(f"Training {name} model...")
        algo.fit(trainset)
        
        print(f"Saving model to {name}_model.pkl...")
        with open(f'{name}_model.pkl', 'wb') as f:
            pickle.dump(algo, f)
            
    print("All models training complete!")

if __name__ == "__main__":
    train_and_save_model()
