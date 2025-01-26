import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
ratings = pd.read_csv('ml-100k/u.data', sep='\t', names=['user_id', 'item_id', 'rating', 'timestamp'])
movies = pd.read_csv('ml-100k/u.item', sep='|', encoding='latin-1',
                     names=['item_id', 'title', 'release_date', 'video_release_date', 'IMDb_URL',
                            'unknown', 'Action', 'Adventure', 'Animation', 'Children', 'Comedy',
                            'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror',
                            'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'])
user_item_matrix = ratings.pivot(index='user_id', columns='item_id', values='rating')
user_item_matrix.fillna(0, inplace=True)
user_similarity = cosine_similarity(user_item_matrix)
user_similarity_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)
def recommend_collaborative(user_id, top_n=5):
    similar_users = user_similarity_df[user_id].sort_values(ascending=False).index[1:]
    recommendations = {}
    for similar_user in similar_users:
        user_ratings = user_item_matrix.loc[similar_user]
        unseen_movies = user_ratings[user_ratings > 0].index.difference(user_item_matrix.loc[user_id][user_item_matrix.loc[user_id] > 0].index)
        for movie_id in unseen_movies:
            recommendations[movie_id] = recommendations.get(movie_id, 0) + user_ratings[movie_id]
        if len(recommendations) >= top_n:
            break
    recommended_movie_ids = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [movies[movies['item_id'] == movie_id]['title'].values[0] for movie_id, _ in recommended_movie_ids]

movies['genres'] = movies.iloc[:, 5:].apply(lambda row: ' '.join(row[row == 1].index), axis=1)
tfidf = TfidfVectorizer()
genre_matrix = tfidf.fit_transform(movies['genres'])
cosine_sim = cosine_similarity(genre_matrix, genre_matrix)
def recommend_content_based(movie_title, top_n=5):
    if movie_title not in movies['title'].values:
        print(f"Movie '{movie_title}' not found in the dataset!")
        return []
   
    movie_idx = movies[movies['title'] == movie_title].index
    if movie_idx.empty:
        print(f"Movie '{movie_title}' not found in the dataset!")
        return []
   
    movie_idx = movie_idx[0]
    sim_scores = list(enumerate(cosine_sim[movie_idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    top_movies = [movies.iloc[i[0]]['title'] for i in sim_scores[1:top_n+1]]
    return top_movies
def hybrid_recommend(user_id, movie_title, top_n=5):
    cb_recs = recommend_content_based(movie_title, top_n)
    cf_recs = recommend_collaborative(user_id, top_n)
    hybrid_recs = list(set(cb_recs + cf_recs))
    return hybrid_recs[:top_n]
movies['title'] = movies['title'].str.strip()
movie='Jumanji (1995)'
print("\nContent-Based Recommendations for 'Star Wars (1977)':", recommend_content_based(movie, top_n=5))
print("\nCollaborative Recommendations for User 1:", recommend_collaborative(user_id=1, top_n=5))
print("\nHybrid Recommendations for User 1 based on 'Star Wars (1977)':", hybrid_recommend(user_id=1, movie_title=movie, top_n=5))