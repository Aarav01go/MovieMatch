import pandas as pd
from surprise import Dataset, Reader, SVD
import pickle

def train_and_save_model():
    print("Loading data...")
    ratings = pd.read_csv('ratings.csv')
    
    reader = Reader(rating_scale=(0.5, 5.0))
    data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)
    
    print("Building full trainset...")
    trainset = data.build_full_trainset()
    
    print("Training SVD model...")
    algo = SVD()
    algo.fit(trainset)
    
    print("Saving model to svd_model.pkl...")
    with open('svd_model.pkl', 'wb') as f:
        pickle.dump(algo, f)
        
    print("Model training complete!")

if __name__ == "__main__":
    train_and_save_model()
