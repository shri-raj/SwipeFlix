from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
sys.path.append('.')
from recommenders import MovieRecommender

app = Flask(__name__)
CORS(app)

recommender = MovieRecommender('ml-100k/u.data', 'ml-100k/u.item')

@app.route('/swipe', methods=['POST'])
def record_swipe():
    data = request.json
    try:
        recommender.record_swipe(
            user_id=data['user_id'], 
            movie_title=data['movie_title'], 
            swipe_type=data['swipe_type']
        )
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    user_id = request.args.get('user_id', type=int)
    last_swiped_movie = request.args.get('last_swiped_movie')
    
    try:
        recommendations = recommender.swipe_style_recommend(
            user_id=user_id, 
            last_swiped_movie=last_swiped_movie
        )
        return jsonify({
            "recommendations": recommendations
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/movies', methods=['GET'])
def get_movies():
    movies = recommender.movies[['title', 'release_date', 'genres']].to_dict(orient='records')

    return jsonify({"movies": movies}), 200

if __name__ == '__main__':
    app.run(debug=True)