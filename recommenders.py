import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

class MovieRecommender:
    def __init__(self, ratings_path, movies_path):
        self.ratings = pd.read_csv(ratings_path, sep='\t', names=['user_id', 'item_id', 'rating', 'timestamp'])
        self.movies = pd.read_csv(movies_path, sep='|', encoding='latin-1',
                     names=['item_id', 'title', 'release_date', 'video_release_date', 'IMDb_URL',
                            'unknown', 'Action', 'Adventure', 'Animation', 'Children', 'Comedy',
                            'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror',
                            'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'])
        
        # Preprocess movies
        self.movies['title'] = self.movies['title'].str.strip()
        self.movies['genres'] = self.movies.iloc[:, 5:].apply(lambda row: ' '.join(row[row == 1].index), axis=1)
        
        # Prepare matrices
        self.user_item_matrix = self.ratings.pivot(index='user_id', columns='item_id', values='rating')
        self.user_item_matrix.fillna(0, inplace=True)
        
        # User similarity
        self.user_similarity = cosine_similarity(self.user_item_matrix)
        self.user_similarity_df = pd.DataFrame(self.user_similarity, 
                                               index=self.user_item_matrix.index, 
                                               columns=self.user_item_matrix.index)
        
        # Content-based similarity
        self.tfidf = TfidfVectorizer()
        self.genre_matrix = self.tfidf.fit_transform(self.movies['genres'])
        self.cosine_sim = cosine_similarity(self.genre_matrix, self.genre_matrix)
        
        # Swipe history
        self.swipe_history = {}
    
    def record_swipe(self, user_id, movie_title, swipe_type):
        """
        Record user's swipe (like/dislike) for a movie
        
        :param user_id: User identifier
        :param movie_title: Movie title
        :param swipe_type: 'like' or 'dislike'
        """
        if user_id not in self.swipe_history:
            self.swipe_history[user_id] = {
                'liked_movies': [],
                'disliked_movies': []
            }
        
        if swipe_type == 'like':
            self.swipe_history[user_id]['liked_movies'].append(movie_title)
        else:
            self.swipe_history[user_id]['disliked_movies'].append(movie_title)
    
    def get_user_liked_genres(self, user_id):
        """
        Extract genres from user's liked movies
        
        :param user_id: User identifier
        :return: List of genres liked by the user
        """
        if user_id not in self.swipe_history:
            return []
        
        liked_movies = self.swipe_history[user_id]['liked_movies']
        liked_genres = self.movies[self.movies['title'].isin(liked_movies)]['genres'].tolist()
        return liked_genres
    
    def recommend_content_based(self, movie_title, top_n=5):
        """
        Recommend movies similar to a given movie based on genres
        
        :param movie_title: Base movie title
        :param top_n: Number of recommendations
        :return: List of recommended movie titles
        """
        if movie_title not in self.movies['title'].values:
            return []
        
        movie_idx = self.movies[self.movies['title'] == movie_title].index[0]
        sim_scores = list(enumerate(self.cosine_sim[movie_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        return [self.movies.iloc[i[0]]['title'] for i in sim_scores[1:top_n+1]]
    
    def recommend_collaborative(self, user_id, top_n=5):
        """
        Recommend movies based on similar users' ratings
        
        :param user_id: User identifier
        :param top_n: Number of recommendations
        :return: List of recommended movie titles
        """
        similar_users = self.user_similarity_df[user_id].sort_values(ascending=False).index[1:]
        recommendations = {}
        
        for similar_user in similar_users:
            user_ratings = self.user_item_matrix.loc[similar_user]
            unseen_movies = user_ratings[user_ratings > 0].index.difference(
                self.user_item_matrix.loc[user_id][self.user_item_matrix.loc[user_id] > 0].index)
            
            for movie_id in unseen_movies:
                recommendations[movie_id] = recommendations.get(movie_id, 0) + user_ratings[movie_id]
            
            if len(recommendations) >= top_n:
                break
        
        recommended_movie_ids = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return [self.movies[self.movies['item_id'] == movie_id]['title'].values[0] for movie_id, _ in recommended_movie_ids]
    
    def swipe_style_recommend(self, user_id, last_swiped_movie=None, top_n=5):
        """
        Generate Tinder-style recommendations considering user's swipe history
        
        :param user_id: User identifier
        :param last_swiped_movie: Most recently swiped movie
        :param top_n: Number of recommendations
        :return: List of recommended movie titles
        """
        if user_id not in self.swipe_history or not self.swipe_history[user_id]['liked_movies']:
            return self.recommend_collaborative(user_id, top_n)
        
        content_recs = (self.recommend_content_based(last_swiped_movie, top_n) 
                        if last_swiped_movie 
                        else self.recommend_content_based(self.swipe_history[user_id]['liked_movies'][0], top_n))
        
        collab_recs = self.recommend_collaborative(user_id, top_n)
        
        hybrid_recs = list(dict.fromkeys(content_recs + collab_recs))
        
        return hybrid_recs[:top_n]

recommender = MovieRecommender('ml-100k/u.data', 'ml-100k/u.item')

recommender.record_swipe(user_id=1, movie_title='Star Wars (1977)', swipe_type='like')
recommender.record_swipe(user_id=1, movie_title='Jurassic Park (1993)', swipe_type='dislike')

recommendations = recommender.swipe_style_recommend(user_id=1, last_swiped_movie='Star Wars (1977)')
print("Recommendations:", recommendations)