import React, { useRef, useState, useEffect } from 'react';
import Webcam from 'react-webcam';
import * as faceapi from '@vladmandic/face-api';

const FaceCapture = ({ onCapture }) => {
  const webcamRef = useRef(null);
  const [isFaceDetected, setIsFaceDetected] = useState(false);
  const [modelLoaded, setModelLoaded] = useState(false);
  const [error, setError] = useState('');

  // Load the face detection models
  useEffect(() => {
    const loadModels = async () => {
      // The '/models' path is relative to the public folder
      const modelPath = '/models'; 
      try {
        console.log("Loading face-api models...");
        await faceapi.nets.tinyFaceDetector.loadFromUri(modelPath);
        setModelLoaded(true);
        console.log("Models loaded successfully.");
      } catch (e) {
        setError("Could not load face detection models.");
        console.error("Error loading models:", e);
      }
    };
    loadModels();
  }, []);

  // Detect faces in a loop
  const handleVideoPlay = () => {
    const detectionInterval = setInterval(async () => {
      if (webcamRef.current && webcamRef.current.video) {
        const video = webcamRef.current.video;
        const detections = await faceapi.detectAllFaces(
          video,
          new faceapi.TinyFaceDetectorOptions()
        );
        
        setIsFaceDetected(detections.length > 0);
      }
    }, 500); // Check for a face every 500ms
    
    // Cleanup the interval when the component unmounts
    return () => clearInterval(detectionInterval);
  };

  const handleCapture = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    fetch(imageSrc)
      .then(res => res.blob())
      .then(blob => onCapture(blob));
  };

  return (
    <div>
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        width={320}
        height={240}
        onUserMedia={handleVideoPlay} // Start detection once the camera is ready
      />
      <br />
      <button type="button" onClick={handleCapture} disabled={!isFaceDetected || !modelLoaded}>
        {modelLoaded ? (isFaceDetected ? 'Capture Face Template' : 'No Face Detected') : 'Loading Models...'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default FaceCapture;