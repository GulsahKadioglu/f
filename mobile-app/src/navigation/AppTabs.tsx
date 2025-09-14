import React from "react";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createStackNavigator } from "@react-navigation/stack";

// Import screens used in the navigators
import HomeScreen from "../screens/HomeScreen";
import ReportDetailScreen from "../screens/ReportDetailScreen";
import CasesScreen from "../screens/CasesScreen";
import CreateCaseScreen from "../screens/CreateCaseScreen";
import CaseDetailScreen from "../screens/CaseDetailScreen";
import ProfileScreen from "../screens/ProfileScreen";

const Tab = createBottomTabNavigator();
const ReportStack = createStackNavigator();
const CaseStack = createStackNavigator();

/**
 * ReportNavigator component.
 *
 * This is a stack navigator specifically for the "Reports" tab.
 * It defines the screens that can be navigated to within the Reports section
 * and manages their navigation history.
 *
 * @returns {JSX.Element} A stack navigator for reports, containing Home and ReportDetail screens.
 */
function ReportNavigator() {
  return (
    <ReportStack.Navigator>
      <ReportStack.Screen
        name="Home"
        component={HomeScreen}
        options={{ title: "Analysis Reports" }}
      />
      <ReportStack.Screen
        name="ReportDetail"
        component={ReportDetailScreen}
        options={{ title: "Report Detail" }}
      />
    </ReportStack.Navigator>
  );
}

/**
 * CaseNavigator component.
 *
 * This is a stack navigator specifically for the "Cases" tab.
 * It manages the navigation flow between the list of medical cases, the screen
 * for creating new cases, and the detailed view of a specific case.
 *
 * @returns {JSX.Element} A stack navigator for medical cases, containing CasesList, CreateCase, and CaseDetail screens.
 */
function CaseNavigator() {
  return (
    <CaseStack.Navigator>
      <CaseStack.Screen
        name="CasesList"
        component={CasesScreen}
        options={{ title: "Cases" }}
      />
      <CaseStack.Screen
        name="CreateCase"
        component={CreateCaseScreen}
        options={{ title: "Create New Case" }}
      />
      <CaseStack.Screen
        name="CaseDetail"
        component={CaseDetailScreen}
        options={{ title: "Case Detail" }}
      />
    </CaseStack.Navigator>
  );
}

/**
 * AppTabs component.
 *
 * This component defines the bottom tab navigation for the application.
 * It includes tabs for Reports, Cases, and Profile, each linked to its
 * respective navigator (for Reports and Cases) or a direct screen (for Profile).
 *
 * @returns {JSX.Element} A tab navigator for the main application sections.
 */
const AppTabs = () => {
  return (
    <Tab.Navigator>
      <Tab.Screen
        name="Reports"
        component={ReportNavigator}
        options={{ title: "Reports", headerShown: false }}
      />
      <Tab.Screen
        name="Cases"
        component={CaseNavigator}
        options={{ title: "Cases", headerShown: false }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{ title: "Profile" }}
      />
    </Tab.Navigator>
  );
};

export default AppTabs;
