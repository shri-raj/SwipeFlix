import React, { useState, useEffect } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";

const App = () => {
  const [movies, setMovies] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        const response = await axios.get("http://localhost:5000/movies");
        setMovies(response.data.movies);
      } catch (error) {
        console.error("Error fetching movies:", error);
      }
    };
    fetchMovies();
  }, []);

  const handleSwipe = async (swipeType) => {
    if (currentIndex >= movies.length) return;
    const movieTitle = movies[currentIndex].title;
    const userId = 1;
    try {
      await axios.post("http://localhost:5000/swipe", {
        user_id: userId,
        movie_title: movieTitle,
        swipe_type: swipeType,
      });
      setCurrentIndex((prevIndex) => prevIndex + 1);
    } catch (error) {
      console.error("Error recording swipe:", error);
    }
  };

  const currentMovie = movies[currentIndex];

  const handleDragEnd = (event, info) => {
    const swipeThreshold = 100;
    if (info.offset.x > swipeThreshold) {
      handleSwipe("like");
    } else if (info.offset.x < -swipeThreshold) {
      handleSwipe("dislike");
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-custom p-4">
      <div className="w-full max-w-md">
        <h1 className="text-2xl font-bold mb-4 text-center px-5 text-custom">SwipeFlix 🎥</h1>
        <div className="flex justify-center align-center items-center">
          <AnimatePresence>
            {currentMovie && (
              <motion.div
                key={currentIndex}
                className="w-full max-w-xs h-96 bg-grey rounded-xl shadow-lg 
                  border-8 border-custom flex flex-col items-center justify-center p-4"
                drag="x"
                onDragEnd={handleDragEnd}
                dragElastic={0.7}
                dragConstraints={{ left: -250, right: 250 }}
                initial={{ opacity: 0, x: 0, scale: 0.8 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: -300, scale: 0.8 }}
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                align="center"
                justify="center"
              >
                <h2 className="text-xl font-semibold mb-2 text-center text-custom">{currentMovie.title.split("(")[0]}</h2>
                <p className="text-custom mb-1">Year: {currentMovie.release_date.split("-")[2]}</p>
                <p className="text-custom">Genres: {currentMovie.genres}</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        {!currentMovie && (
          <p className="text-custom text-center mt-20">No more movies. Refresh to see more!</p>
        )}
      </div>
    </div>
  );
};

export default App;