import React from 'react';
import { View, Text, StyleSheet, ScrollView, Image } from 'react-native';
import { Button, Title, Paragraph } from 'react-native-paper';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface OnboardingScreenProps {
  navigation: any;
}

const OnboardingScreen: React.FC<OnboardingScreenProps> = ({ navigation }) => {
  const handleFinishOnboarding = async () => {
    await AsyncStorage.setItem('hasViewedOnboarding', 'true');
    navigation.replace('Auth'); // Navigate to Auth stack (Login/Register)
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Image source={require('../../assets/onboarding_welcome.png')} style={styles.image} />
        <Title style={styles.title}>Hoş Geldiniz!</Title>
        <Paragraph style={styles.paragraph}>
          Federasyon Tabanlı Kanser Tarama uygulamasına hoş geldiniz. Bu uygulama, tıbbi görüntülerinizi güvenli ve gizli bir şekilde analiz ederek kanser tarama sonuçlarınızı takip etmenizi sağlar.
        </Paragraph>
      </View>

      <View style={styles.section}>
        <Image source={require('../../assets/onboarding_privacy.png')} style={styles.image} />
        <Title style={styles.title}>Gizliliğiniz Önceliğimiz</Title>
        <Paragraph style={styles.paragraph}>
          Verileriniz en yüksek güvenlik standartlarıyla korunmaktadır. Görüntüleriniz şifrelenir ve kimliğinizden arındırılır. Yapay zeka modelleri, verilerinizin gizliliğini koruyarak eğitilir.
        </Paragraph>
      </View>

      <View style={styles.section}>
        <Image source={require('../../assets/onboarding_results.png')} style={styles.image} />
        <Title style={styles.title}>Sonuçlarınızı Kolayca Takip Edin</Title>
        <Paragraph style={styles.paragraph}>
          Tarama sonuçlarınızı uygulama üzerinden kolayca görüntüleyebilir, geçmiş raporlarınıza erişebilir ve doktorunuzla paylaşabilirsiniz.
        </Paragraph>
      </View>

      <Button mode="contained" onPress={handleFinishOnboarding} style={styles.button}>
        Başlayın
      </Button>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 20,
  },
  section: {
    marginBottom: 40,
    alignItems: 'center',
  },
  image: {
    width: 200,
    height: 200,
    resizeMode: 'contain',
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
  },
  paragraph: {
    fontSize: 16,
    textAlign: 'center',
    lineHeight: 24,
    color: '#555',
  },
  button: {
    marginTop: 20,
    marginBottom: 40,
    paddingVertical: 10,
  },
});

export default OnboardingScreen;
