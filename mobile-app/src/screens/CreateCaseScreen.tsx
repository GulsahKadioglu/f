/**
 * CreateCaseScreen.tsx
 *
 * This screen provides a user interface for creating a new medical case.
 * Users can input a patient ID, select a case date using a date picker,
 * and choose a status for the case. The entered data is then sent to the
 * backend API to create the new medical case record.
 *
 * Purpose:
 * - To facilitate the creation of new medical case entries in the system.
 * - To collect essential information for a medical case from the user.
 * - To handle form input, date selection, and status assignment.
 * - To communicate with the backend API for case creation.
 *
 * Key Components:
 * - `useState`: React hook for managing component state (patient ID, date, status, loading).
 * - `TextInput`, `Button`, `Text`, `RadioButton`: UI components from `react-native-paper`
 *   for form input and actions.
 * - `DateTimePicker`: Component for selecting dates.
 * - `apiClient`: Custom service for making authenticated API calls to the backend.
 *
 * Data Flow:
 * - User inputs `patientId` and selects `caseDate` and `status`.
 * - `onDateChange` updates the selected date.
 * - `handleCreateCase` validates input and sends a POST request to `/api/v1/cases/`.
 * - Navigation (`navigation.goBack()`) returns to the previous screen on success.
 */

import React, { useState } from "react";
import { View, StyleSheet, Alert } from "react-native";
import { TextInput, Button, Text, RadioButton } from "react-native-paper";
import DateTimePicker from "@react-native-community/datetimepicker";
import apiClient from "../services/api";

/**
 * CreateCaseScreen component.
 *
 * This screen provides a form for users to input details for a new medical case,
 * including a patient ID, case date, and status. It handles form submission
 * and communicates with the backend API to create the case.
 *
 * @param {object} props - Component props.
 * @param {object} props.navigation - The navigation object from React Navigation.
 * @returns {JSX.Element} The Create Case screen.
 */
const CreateCaseScreen = ({ navigation }) => {
  const [patientId, setPatientId] = useState("");
  const [caseDate, setCaseDate] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [status, setStatus] = useState("Active"); // Initial status
  const [loading, setLoading] = useState(false);

  const onDateChange = (event, selectedDate) => {
    const currentDate = selectedDate || caseDate;
    setShowDatePicker(false);
    setCaseDate(currentDate);
  };

  /**
   * Handles the submission of the new medical case form.
   *
   * Validates the input, sends a POST request to the backend API to create
   * the case, and provides feedback to the user. Navigates back to the
   * previous screen on success.
   */
  const handleCreateCase = async () => {
    if (!patientId || !caseDate) {
      Alert.alert("Error", "Please fill in all fields.");
      return;
    }

    setLoading(true);
    try {
      const formattedDate = caseDate.toISOString().split("T")[0];
      await apiClient.post("/api/v1/cases/", {
        patient_id: patientId,
        case_date: formattedDate,
        status: status,
      });
      Alert.alert("Success", "New case successfully created.");
      navigation.goBack();
    } catch (error) {
      console.error(
        "Error creating case:",
        error.response?.data || error.message,
      );
      Alert.alert("Error", "An issue occurred while creating the case.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <TextInput
        label="Patient ID (Anonymous)"
        value={patientId}
        onChangeText={setPatientId}
        style={styles.input}
        mode="outlined"
      />

      <View style={styles.datePickerContainer}>
        <TextInput
          label="Case Date"
          value={caseDate.toLocaleDateString()}
          onFocus={() => setShowDatePicker(true)}
          style={styles.input}
          mode="outlined"
          showSoftInputOnFocus={false}
        />
        {showDatePicker && (
          <DateTimePicker
            value={caseDate}
            mode="date"
            display="default"
            onChange={onDateChange}
          />
        )}
      </View>

      <Text style={styles.radioGroupLabel}>Status:</Text>
      <RadioButton.Group
        onValueChange={(newValue) => setStatus(newValue)}
        value={status}
      >
        <View style={styles.radioButtonRow}>
          <RadioButton value="Active" />
          <Text>Active</Text>
        </View>
        <View style={styles.radioButtonRow}>
          <RadioButton value="Pending" />
          <Text>Pending</Text>
        </View>
        <View style={styles.radioButtonRow}>
          <RadioButton value="Closed" />
          <Text>Closed</Text>
        </View>
      </RadioButton.Group>

      <Button
        mode="contained"
        onPress={handleCreateCase}
        loading={loading}
        style={styles.button}
      >
        Create Case
      </Button>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: "#f5f5f5",
  },
  input: {
    marginBottom: 15,
  },
  datePickerContainer: {
    marginBottom: 15,
  },
  radioGroupLabel: {
    fontSize: 16,
    color: "#333",
    marginBottom: 10,
  },
  radioButtonRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 5,
  },
  button: {
    marginTop: 20,
  },
});

export default CreateCaseScreen;
