/**
 * CaseDetailScreen.tsx
 *
 * This screen displays the detailed information of a specific medical case within the
 * mobile application. It fetches and presents patient details, case status, and a list
 * of associated medical images. Users can also upload new images to the case directly
 * from this screen.
 *
 * Purpose:
 * - To provide a comprehensive view of a single medical case.
 * - To allow users to upload new diagnostic images related to the case.
 * - To manage the loading and error states during data fetching and image uploads.
 *
 * Key Components:
 * - `useState`, `useEffect`, `useCallback`: React hooks for managing component state,
 *   side effects, and memoizing functions.
 * - `@react-navigation/native`: For accessing navigation parameters (`route`) and `useFocusEffect`.
 * - `expo-image-picker`: For interacting with the device's media library to select images.
 * - `apiClient`: Custom service for making authenticated API calls to the backend.
 * - `react-native-paper`: UI components (Button, Card, Title, Paragraph, Text, ActivityIndicator).
 * - `FlatList`: For efficiently rendering lists of medical images.
 *
 * Data Flow:
 * - `caseId` is received via navigation parameters.
 * - `fetchCaseDetails` fetches case data from the backend API.
 * - `handleImagePick` initiates the image selection process.
 * - `uploadImage` sends the selected image to the backend API.
 * - State variables (`caseDetails`, `loading`, `uploading`, `error`) manage UI rendering.
 */

import React, { useState, useCallback } from "react";
import {
  View,
  StyleSheet,
  FlatList,
  Image,
  Alert,
  ActivityIndicator,
  ScrollView,
} from "react-native";
import { Button, Card, Title, Paragraph, Text } from "react-native-paper";
import * as ImagePicker from "expo-image-picker";
import apiClient from "../services/api";
import { useFocusEffect } from "@react-navigation/native";

/**
 * CaseDetailScreen component.
 *
 * Displays the detailed information for a medical case, including its status,
 * patient ID, and a list of associated medical images. Users can upload new
 * mammogram images to the case from this screen.
 *
 * @param {object} props - Component props.
 * @param {object} props.route - The route object containing navigation parameters.
 * @param {string} props.route.params.caseId - The ID of the medical case to display.
 * @returns {JSX.Element} The Case Detail screen.
 */
const CaseDetailScreen = ({ route }) => {
  const { caseId } = route.params;
  const [caseDetails, setCaseDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const fetchCaseDetails = useCallback(async () => {
    setLoading(true);
    try {
      const response = await apiClient.get(`/api/v1/cases/${caseId}`);
      setCaseDetails(response.data);
    } catch (err) {
      setError("An error occurred while loading case details.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      fetchCaseDetails();
    }, [fetchCaseDetails]),
  );

  /**
   * Handles the image picking process from the device's media library.
   *
   * It requests media library permissions, launches the image picker, and
   * if an image is selected, calls `uploadImage` to send it to the backend.
   */
  const handleImagePick = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== "granted") {
      Alert.alert(
        "Permission Required",
        "We need gallery access to upload images!",
      );
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: false,
      quality: 1,
    });

    if (!result.canceled) {
      uploadImage(result.assets[0].uri);
    }
  };

  /**
   * Uploads the selected image to the backend for the current medical case.
   *
   * It constructs a FormData object with the image file and sends it via a POST request.
   * Upon successful upload, it refreshes the case details.
   *
   * @param {string} uri - The URI of the image to upload.
   */
  const uploadImage = async (uri: string) => {
    setUploading(true);
    try {
      const formData = new FormData();
      const uriParts = uri.split(".");
      const fileType = uriParts[uriParts.length - 1];

      formData.append("file", {
        uri,
        name: `image_${Date.now()}.${fileType}`,
        type: `image/${fileType}`,
      });

      await apiClient.post(`/api/v1/cases/${caseId}/images`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      Alert.alert("Success", "Image uploaded successfully.");
      fetchCaseDetails();
    } catch (err) {
      console.error("Image upload error:", err.response?.data || err.message);
      Alert.alert(
        "Upload Failed",
        "An issue occurred while uploading the image.",
      );
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator animating={true} size="large" />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>{error}</Text>
      </View>
    );
  }

  if (!caseDetails) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>Case not found.</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.title}>Case Details: #{caseDetails.id}</Title>

          <View style={styles.detailRow}>
            <Text style={styles.label}>Patient ID:</Text>
            <Text style={styles.value}>{caseDetails.patient_id}</Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.label}>Case Date:</Text>
            <Text style={styles.value}>
              {new Date(caseDetails.case_date).toLocaleDateString()}
            </Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.label}>Status:</Text>
            <Text style={styles.value}>{caseDetails.status}</Text>
          </View>

          <Paragraph style={styles.additionalInfo}>
            Additional notes or detailed descriptions related to the case can be
            added here.
          </Paragraph>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.title}>Images</Title>
          <Button
            mode="contained"
            onPress={handleImagePick}
            loading={uploading}
            style={styles.button}
          >
            Upload Mammogram
          </Button>
          {caseDetails.images && caseDetails.images.length > 0 ? (
            <FlatList
              data={caseDetails.images}
              keyExtractor={(item) => item.id.toString()}
              numColumns={2}
              renderItem={({ item }) => (
                <View style={styles.imageContainer}>
                  <Image
                    source={{ uri: item.image_path }}
                    style={styles.image}
                    alt={`Medical image ${item.id}`}
                  />
                </View>
              )}
              contentContainerStyle={styles.imageList}
            />
          ) : (
            <Text style={styles.noImagesText}>
              No images found for this case yet.
            </Text>
          )}
        </Card.Content>
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: "#f5f5f5",
  },
  centered: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  errorText: {
    color: "red",
    fontSize: 16,
  },
  card: {
    marginVertical: 8,
    borderRadius: 12,
    elevation: 4,
  },
  title: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 15,
    color: "#333",
  },
  detailRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 10,
    paddingBottom: 5,
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },
  label: {
    fontSize: 16,
    fontWeight: "600",
    color: "#555",
  },
  value: {
    fontSize: 16,
    color: "#333",
  },
  additionalInfo: {
    marginTop: 20,
    fontStyle: "italic",
    color: "#777",
  },
  button: {
    marginTop: 15,
    marginBottom: 10,
  },
  imageList: {
    marginTop: 10,
  },
  imageContainer: {
    flex: 1,
    margin: 5,
    alignItems: "center",
  },
  image: {
    width: "100%",
    height: 150,
    borderRadius: 8,
    resizeMode: "cover",
  },
  noImagesText: {
    textAlign: "center",
    marginTop: 20,
    color: "#888",
  },
});

export default CaseDetailScreen;
