import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  VStack,
  Alert,
  AlertIcon,
  Spinner,
  Text,
  Divider,
} from '@chakra-ui/react';
import MCQGenerator from './components/MCQGenerator';
import CourseList from './components/CourseList';
import MCQDisplay from './components/MCQDisplay';
import { getCourses } from './services/api';

function App() {
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState('');
  const [mcqs, setMcqs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [mcqLoading, setMcqLoading] = useState(false);

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      setLoading(true);
      const coursesData = await getCourses();
      setCourses(coursesData);
      setError('');
    } catch (err) {
      setError('Failed to load courses. Please check if the backend is running.');
      console.error('Error loading courses:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCourseSelect = (courseCode) => {
    setSelectedCourse(courseCode);
    setMcqs([]);
    setError('');
  };

  const handleMcqGenerated = (generatedMcqs) => {
    setMcqs(generatedMcqs);
    setError('');
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
    setMcqs([]);
  };

  return (
    <Box minH="100vh" bg="gray.50">
      <Container maxW="container.xl" py={8}>
        <VStack spacing={8}>
          {/* Header */}
          <Box textAlign="center">
            <Heading size="2xl" color="brand.700" mb={2}>
              Course MCQ Generator
            </Heading>
            <Text fontSize="lg" color="gray.600">
              Generate multiple-choice questions from course materials using AI
            </Text>
          </Box>

          <Divider />

          {/* Error Alert */}
          {error && (
            <Alert status="error" borderRadius="md">
              <AlertIcon />
              {error}
            </Alert>
          )}

          {/* Main Content */}
          <Box width="100%" maxW="800px">
            <VStack spacing={6}>
              {/* Course Selection */}
              <Box width="100%">
                <Heading size="lg" mb={4} color="gray.700">
                  Available Courses
                </Heading>
                {loading ? (
                  <Box textAlign="center" py={8}>
                    <Spinner size="lg" color="brand.500" />
                    <Text mt={2} color="gray.600">
                      Loading courses...
                    </Text>
                  </Box>
                ) : (
                  <CourseList
                    courses={courses}
                    selectedCourse={selectedCourse}
                    onCourseSelect={handleCourseSelect}
                    onRefresh={loadCourses}
                  />
                )}
              </Box>

              {/* MCQ Generator */}
              {selectedCourse && (
                <Box width="100%">
                  <Heading size="lg" mb={4} color="gray.700">
                    Generate MCQs
                  </Heading>
                  <MCQGenerator
                    selectedCourse={selectedCourse}
                    onMcqGenerated={handleMcqGenerated}
                    onError={handleError}
                    loading={mcqLoading}
                    setLoading={setMcqLoading}
                  />
                </Box>
              )}

              {/* MCQ Display */}
              {mcqs.length > 0 && (
                <Box width="100%">
                  <Heading size="lg" mb={4} color="gray.700">
                    Generated Questions
                  </Heading>
                  <MCQDisplay mcqs={mcqs} courseCode={selectedCourse} />
                </Box>
              )}
            </VStack>
          </Box>
        </VStack>
      </Container>
    </Box>
  );
}

export default App;