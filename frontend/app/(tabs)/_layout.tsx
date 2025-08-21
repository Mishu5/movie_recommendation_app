import React from 'react';
import { Tabs } from 'expo-router';

const TabLayout = () => {
    return (
        <Tabs screenOptions={{ headerShown: false }}>
            <Tabs.Screen
                name="index"
                options={{ title: 'Home', tabBarIcon: () => <span>🏠</span> }}
            />
            <Tabs.Screen
                name="userPanel"
                options={{ title: 'User Panel', tabBarIcon: () => <span>👤</span> }}
            />
            <Tabs.Screen
                name="room"
                options={{ title: 'Room', tabBarIcon: () => <span>📺</span> }}
            />
        </Tabs>
    );
};

export default TabLayout;