/**
 * CasesScreen.tsx
 *
 * This screen displays a list of medical cases associated with the authenticated user.
 * It allows users to view a summary of each case, navigate to detailed case views,
 * and create new medical cases. The screen supports refreshing the list by pulling down.
 *
 * Purpose:
 * - To provide an overview of all medical cases managed by the current user.
 * - To enable navigation to `CaseDetailScreen` for in-depth case examination.
 * - To facilitate the creation of new medical cases via `CreateCaseScreen`.
 * - To manage data fetching, loading states, and display an empty state if no cases are found.
 *
 * Key Components:
 * - `useState`, `useCallback`: React hooks for managing component state and memoizing functions.
 * - `useFocusEffect`: React Navigation hook to refetch data when the screen comes into focus.
 * - `FlatList`: For efficiently rendering a scrollable list of medical cases.
 * - `react-native-paper`: UI components (Button, Card, Title, Paragraph, Avatar, FAB, ActivityIndicator).
 * - `apiClient`: Custom service for making authenticated API calls to the backend.
 *
 * Data Flow:
 * - `fetchCases` retrieves the list of medical cases from the backend API.
 * - `cases` state stores the fetched list of medical cases.
 * - `loading` state indicates whether data is currently being fetched.
 * - `renderItem` defines how each medical case item is rendered in the `FlatList`.
 * - Navigation actions (`navigation.navigate`) are used to move to other screens.
 */

import React, { useState, useCallback } from "react";
import { View, FlatList, StyleSheet, Text } from "react-native";
import {
  Card,
  Paragraph,
  Avatar,
  FAB,
  ActivityIndicator,
} from "react-native-paper";
import { useFocusEffect } from "@react-navigation/native";
import apiClient from "../services/api";

interface Case {
  id: string;
  patient_id: string;
  case_date: string;
  status: string;
}

/**
 * CasesScreen component.
 *
 * Displays a list of medical cases fetched from the backend. Users can tap on
 * a case to view its details or use the Floating Action Button (FAB) to
 * create a new medical case. The list can be refreshed by pulling down.
 *
 * @param {object} props - Component props.
 * @param {object} props.navigation - The navigation object from React Navigation.
 * @returns {JSX.Element} The Cases screen.
 */
const CasesScreen = ({ navigation }) => {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetches the list of medical cases from the backend.
   *
   * Sets the loading state, makes an API call, and updates the `cases` state.
   * Handles potential errors during the fetch operation.
   */
  const fetchCases = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get("/api/v1/cases/");
      setCases(response.data);
      setError(null);
    } catch (error) {
      console.error(error);
      setError("Failed to load cases.");
    } finally {
      setLoading(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchCases();
    }, []),
  );

  /**
   * Renders an individual item in the FlatList of medical cases.
   *
   * @param {object} params - Parameters for rendering the item.
   * @param {object} params.item - The medical case object to render.
   * @returns {JSX.Element} A Card component displaying case information.
   */
  const renderItem = useCallback(
    ({ item }) => (
      <Card
        style={styles.card}
        onPress={() => navigation.navigate("CaseDetail", { caseId: item.id })}
      >
        <Card.Title
          title={`Case #${item.id}`}
          subtitle={`Patient ID: ${item.patient_id}`}
          left={(props) => <Avatar.Icon {...props} icon="folder-account" />}
        />
        <Card.Content>
          <Paragraph>
            Case Date: {new Date(item.case_date).toLocaleDateString()}
          </Paragraph>
          <Paragraph>
            Status:{" "}
            <Text style={styles.status}>{item.status || "Unknown"}</Text>
          </Paragraph>
        </Card.Content>
      </Card>
    ),
    [navigation],
  );

  if (loading && cases.length === 0) {
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

  return (
    <View style={styles.container}>
      {cases.length === 0 ? (
        <View style={styles.centered}>
          <Text style={styles.emptyText}>No case records found yet.</Text>
        </View>
      ) : (
        <FlatList
          data={cases}
          renderItem={renderItem}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.list}
          onRefresh={fetchCases}
          refreshing={loading}
        />
      )}
      <FAB
        style={styles.fab}
        icon="plus"
        onPress={() => navigation.navigate("CreateCase")}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
  },
  list: {
    padding: 16,
  },
  card: {
    marginVertical: 8,
    borderRadius: 12,
    elevation: 4,
  },
  fab: {
    position: "absolute",
    margin: 16,
    right: 0,
    bottom: 0,
  },
  centered: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  emptyText: {
    fontSize: 18,
    color: "#888",
  },
  status: {
    fontWeight: "bold",
    color: "#007bff",
  },
});

export default CasesScreen;
