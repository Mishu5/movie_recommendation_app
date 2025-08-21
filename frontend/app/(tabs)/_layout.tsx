import React from 'react';
import { Tabs } from 'expo-router';

const TabLayout = () => {
    return (
        <Tabs screenOptions={{ headerShown: false }}>
            <Tabs.Screen
            name="index"
            options={{ title: 'Home', tabBarIcon: () => <span>🏠</span> }}
            />
        </Tabs>
    );
};

export default TabLayout;