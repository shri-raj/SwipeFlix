import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";

const App = () => {
  const [movies, setMovies] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const userId = 1;

  // Fetch initial random movies
  const fetchMovies = useCallback(async () => {
    try {
      const response = await axios.get("http://localhost:5000/movies");
      setMovies(prev => [...prev, ...response.data.movies]);
    } catch (error) {
      console.error("Fetch movies error:", error);
    }
  }, []);

  // Fetch recommendations with swipe history
  const fetchRecommendations = useCallback(async () => {
    try {
      const response = await axios.get("http://localhost:5000/recommendations", {
        params: {
          user_id: userId,
          last_swiped_movie: movies[currentIndex - 1]?.title
        }
      });
      
      setMovies(prev => {
        const newMovies = response.data.recommendations.filter(
          newMovie => !prev.some(m => m.title === newMovie.title)
        );
        return [...prev, ...newMovies];
      });
    } catch (error) {
      console.error("Fetch recommendations error:", error);
      await fetchMovies(); // Fallback to initial movies
    }
  }, [currentIndex, movies, userId, fetchMovies]);

  // Initial load
  useEffect(() => {
    fetchMovies().finally(() => setIsLoading(false));
  }, [fetchMovies]);

  // Pre-fetch recommendations when 3 movies left
  useEffect(() => {
    if (movies.length - currentIndex <= 3) {
      fetchRecommendations();
    }
  }, [currentIndex, movies.length, fetchRecommendations]);

  const handleSwipe = async (swipeType) => {
    if (currentIndex >= movies.length) return;

    try {
      await axios.post("http://localhost:5000/swipe", {
        user_id: userId,
        movie_title: movies[currentIndex].title,
        swipe_type: swipeType,
      });

      setCurrentIndex(prev => prev + 1);
    } catch (error) {
      console.error("Swipe error:", error);
    }
  };

  // Reset when reaching end
  const resetStack = () => {
    setCurrentIndex(0);
    setMovies([]);
    fetchMovies();
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="w-full max-w-md">
        <h1 className="text-2xl font-bold mb-4 text-center text-gray-800">SwipeFlix 🎥</h1>
        
        {isLoading ? (
          <p className="text-center text-gray-600">Loading movies...</p>
        ) : (
          <div className="relative h-96">
            <AnimatePresence>
              {movies.slice(currentIndex, currentIndex + 3).map((movie, index) => (
                <motion.div
                  key={movie.title + index}
                  className="absolute w-full h-full bg-white rounded-xl shadow-lg 
                    flex flex-col items-center justify-center p-4 cursor-grab"
                  style={{ zIndex: 3 - index }}
                  drag="x"
                  dragConstraints={{ left: -300, right: 300 }}
                  onDragEnd={(e, { offset }) => {
                    if (Math.abs(offset.x) > 150) {
                      handleSwipe(offset.x > 0 ? "like" : "dislike");
                    }
                  }}
                  initial={{ scale: 1 - (index * 0.1), y: index * 30, opacity: 0.8 }}
                  animate={{ scale: 1 - (index * 0.1), y: index * 30, opacity: 1 }}
                  exit={{ 
                    x: 500, 
                    opacity: 0,
                    transition: { duration: 0.2 }
                  }}
                >
                  <h2 className="text-xl font-semibold mb-2 text-center">
                    {movie.title.split("(")[0]}
                  </h2>
                  <p className="text-gray-600 mb-1">
                    Year: {movie.release_date?.split("-")[2] || "Unknown"}
                  </p>
                  <p className="text-gray-600">
                    Genres: {movie.genres}
                  </p>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}

        {!isLoading && currentIndex >= movies.length && (
          <div className="text-center mt-4">
            <p className="text-gray-600 mb-4">No more movies!</p>
            <button 
              onClick={resetStack}
              className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
            >
              Load New Movies
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;