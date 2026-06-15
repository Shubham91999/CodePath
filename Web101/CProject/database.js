// Simple Database for STEM for Kids Fair Registration
class RegistrationDatabase {
    constructor() {
        this.storageKey = 'stem_fair_registrations';
        this.registrations = this.loadRegistrations();
    }

    // Load registrations from localStorage
    loadRegistrations() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('Error loading registrations:', error);
            return [];
        }
    }

    // Save registrations to localStorage
    saveRegistrations() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.registrations));
            return true;
        } catch (error) {
            console.error('Error saving registrations:', error);
            return false;
        }
    }

    // Add new registration
    addRegistration(registrationData) {
        const registration = {
            id: this.generateId(),
            timestamp: new Date().toISOString(),
            ...registrationData,
            status: 'pending'
        };

        this.registrations.push(registration);
        const saved = this.saveRegistrations();
        
        if (saved) {
            console.log('Registration saved successfully:', registration);
            return { success: true, registration };
        } else {
            return { success: false, error: 'Failed to save registration' };
        }
    }

    // Get all registrations
    getAllRegistrations() {
        return this.registrations;
    }

    // Get registration by ID
    getRegistrationById(id) {
        return this.registrations.find(reg => reg.id === id);
    }

    // Update registration status
    updateRegistrationStatus(id, status) {
        const registration = this.getRegistrationById(id);
        if (registration) {
            registration.status = status;
            registration.updatedAt = new Date().toISOString();
            return this.saveRegistrations();
        }
        return false;
    }

    // Delete registration
    deleteRegistration(id) {
        const index = this.registrations.findIndex(reg => reg.id === id);
        if (index !== -1) {
            this.registrations.splice(index, 1);
            return this.saveRegistrations();
        }
        return false;
    }

    // Get registration statistics
    getStatistics() {
        const total = this.registrations.length;
        const pending = this.registrations.filter(reg => reg.status === 'pending').length;
        const confirmed = this.registrations.filter(reg => reg.status === 'confirmed').length;
        const cancelled = this.registrations.filter(reg => reg.status === 'cancelled').length;

        // Age distribution
        const ageGroups = {
            '6-8': 0,
            '9-11': 0,
            '12-14': 0
        };

        this.registrations.forEach(reg => {
            const age = parseInt(reg.childAge);
            if (age >= 6 && age <= 8) ageGroups['6-8']++;
            else if (age >= 9 && age <= 11) ageGroups['9-11']++;
            else if (age >= 12 && age <= 14) ageGroups['12-14']++;
        });

        // Interest distribution
        const interests = {};
        this.registrations.forEach(reg => {
            if (reg.interests) {
                reg.interests.forEach(interest => {
                    interests[interest] = (interests[interest] || 0) + 1;
                });
            }
        });

        return {
            total,
            pending,
            confirmed,
            cancelled,
            ageGroups,
            interests
        };
    }

    // Search registrations
    searchRegistrations(query) {
        const searchTerm = query.toLowerCase();
        return this.registrations.filter(reg => 
            reg.parentName.toLowerCase().includes(searchTerm) ||
            reg.childName.toLowerCase().includes(searchTerm) ||
            reg.email.toLowerCase().includes(searchTerm) ||
            reg.phone.includes(searchTerm)
        );
    }

    // Export registrations as CSV
    exportToCSV() {
        if (this.registrations.length === 0) {
            return 'No registrations to export';
        }

        const headers = [
            'ID', 'Parent Name', 'Email', 'Phone', 'Child Name', 'Child Age',
            'Interests', 'Additional Children', 'Status', 'Registration Date'
        ];

        const csvContent = [
            headers.join(','),
            ...this.registrations.map(reg => [
                reg.id,
                `"${reg.parentName}"`,
                `"${reg.email}"`,
                `"${reg.phone}"`,
                `"${reg.childName}"`,
                reg.childAge,
                `"${reg.interests ? reg.interests.join('; ') : ''}"`,
                `"${reg.additionalChildren || ''}"`,
                reg.status,
                new Date(reg.timestamp).toLocaleDateString()
            ].join(','))
        ].join('\n');

        return csvContent;
    }

    // Download CSV file
    downloadCSV() {
        const csv = this.exportToCSV();
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `stem_fair_registrations_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    // Generate unique ID
    generateId() {
        return 'reg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    // Clear all registrations (for testing)
    clearAllRegistrations() {
        this.registrations = [];
        return this.saveRegistrations();
    }

    // Get registrations by date range
    getRegistrationsByDateRange(startDate, endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        return this.registrations.filter(reg => {
            const regDate = new Date(reg.timestamp);
            return regDate >= start && regDate <= end;
        });
    }

    // Get recent registrations (last N days)
    getRecentRegistrations(days = 7) {
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - days);
        
        return this.registrations.filter(reg => 
            new Date(reg.timestamp) >= cutoffDate
        );
    }
}

// Create global database instance
window.registrationDB = new RegistrationDatabase();

// Admin panel functions (for testing and management)
window.adminPanel = {
    // Show all registrations in console
    showAllRegistrations() {
        console.table(window.registrationDB.getAllRegistrations());
    },

    // Show statistics
    showStatistics() {
        const stats = window.registrationDB.getStatistics();
        console.log('Registration Statistics:', stats);
        return stats;
    },

    // Export data
    exportData() {
        window.registrationDB.downloadCSV();
    },

    // Search registrations
    search(query) {
        const results = window.registrationDB.searchRegistrations(query);
        console.table(results);
        return results;
    },

    // Clear all data (use with caution!)
    clearAll() {
        if (confirm('Are you sure you want to clear all registration data?')) {
            window.registrationDB.clearAllRegistrations();
            console.log('All registration data cleared');
        }
    }
};

// Console helper messages
console.log('STEM Fair Database loaded!');
console.log('Available admin commands:');
console.log('- adminPanel.showAllRegistrations() - View all registrations');
console.log('- adminPanel.showStatistics() - View statistics');
console.log('- adminPanel.exportData() - Download CSV export');
console.log('- adminPanel.search("query") - Search registrations');
console.log('- adminPanel.clearAll() - Clear all data (use with caution!)');

// Test function to verify database is working
window.testDatabase = function() {
    console.log('Testing database functionality...');
    
    // Test adding a registration
    const testData = {
        parentName: 'Test Parent',
        email: 'test@example.com',
        phone: '123-456-7890',
        childName: 'Test Child',
        childAge: '8',
        interests: ['science', 'coding'],
        additionalChildren: 'None'
    };
    
    const result = window.registrationDB.addRegistration(testData);
    console.log('Test registration result:', result);
    
    // Test retrieving registrations
    const allRegs = window.registrationDB.getAllRegistrations();
    console.log('All registrations:', allRegs);
    
    // Test statistics
    const stats = window.registrationDB.getStatistics();
    console.log('Statistics:', stats);
    
    return result;
};
