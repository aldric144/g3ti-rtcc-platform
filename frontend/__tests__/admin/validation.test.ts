describe('Admin Form Validation', () => {
  describe('Camera Form Validation', () => {
    const validateCameraForm = (data: Record<string, unknown>) => {
      const errors: Record<string, string> = {};
      if (!data.name || String(data.name).trim() === '') {
        errors.name = 'Camera name is required';
      }
      if (!data.type) {
        errors.type = 'Camera type is required';
      }
      if (!data.lat || !data.lng) {
        errors.location = 'Location is required';
      } else {
        const lat = Number(data.lat);
        const lng = Number(data.lng);
        if (lat < 26.74 || lat > 26.82 || lng < -80.10 || lng > -80.03) {
          errors.location = 'Location must be within Riviera Beach bounds';
        }
      }
      if (data.stream_url && !String(data.stream_url).match(/^(rtsp|http|https):\/\/.+/)) {
        errors.stream_url = 'Invalid stream URL format';
      }
      return errors;
    };

    it('validates required name field', () => {
      const errors = validateCameraForm({ name: '', type: 'fixed', lat: 26.775, lng: -80.058 });
      expect(errors.name).toBe('Camera name is required');
    });

    it('validates required type field', () => {
      const errors = validateCameraForm({ name: 'Test', type: '', lat: 26.775, lng: -80.058 });
      expect(errors.type).toBe('Camera type is required');
    });

    it('validates required location', () => {
      const errors = validateCameraForm({ name: 'Test', type: 'fixed', lat: null, lng: null });
      expect(errors.location).toBe('Location is required');
    });

    it('validates location within Riviera Beach bounds', () => {
      const errors = validateCameraForm({ name: 'Test', type: 'fixed', lat: 25.0, lng: -80.0 });
      expect(errors.location).toBe('Location must be within Riviera Beach bounds');
    });

    it('validates stream URL format', () => {
      const errors = validateCameraForm({ name: 'Test', type: 'fixed', lat: 26.775, lng: -80.058, stream_url: 'invalid' });
      expect(errors.stream_url).toBe('Invalid stream URL format');
    });

    it('passes validation with valid data', () => {
      const errors = validateCameraForm({
        name: 'Test Camera',
        type: 'fixed',
        lat: 26.775,
        lng: -80.058,
        stream_url: 'rtsp://camera.local/stream',
      });
      expect(Object.keys(errors)).toHaveLength(0);
    });
  });

  describe('Drone Form Validation', () => {
    const validateDroneForm = (data: Record<string, unknown>) => {
      const errors: Record<string, string> = {};
      if (!data.drone_id || String(data.drone_id).trim() === '') {
        errors.drone_id = 'Drone ID is required';
      }
      if (!data.model) {
        errors.model = 'Model is required';
      }
      if (!data.serial_number || String(data.serial_number).trim() === '') {
        errors.serial_number = 'Serial number is required';
      }
      return errors;
    };

    it('validates required drone_id field', () => {
      const errors = validateDroneForm({ drone_id: '', model: 'dji_mavic_3', serial_number: 'ABC123' });
      expect(errors.drone_id).toBe('Drone ID is required');
    });

    it('validates required model field', () => {
      const errors = validateDroneForm({ drone_id: 'DRONE-001', model: '', serial_number: 'ABC123' });
      expect(errors.model).toBe('Model is required');
    });

    it('passes validation with valid data', () => {
      const errors = validateDroneForm({
        drone_id: 'RBPD-UAV-001',
        model: 'dji_mavic_3',
        serial_number: 'DJI123456',
      });
      expect(Object.keys(errors)).toHaveLength(0);
    });
  });

  describe('Sector Form Validation', () => {
    const validateSectorForm = (data: Record<string, unknown>) => {
      const errors: Record<string, string> = {};
      if (!data.sector_id || String(data.sector_id).trim() === '') {
        errors.sector_id = 'Sector ID is required';
      }
      if (!data.name || String(data.name).trim() === '') {
        errors.name = 'Name is required';
      }
      const boundary = data.boundary as Array<{ lat: number; lng: number }> | undefined;
      if (!boundary || boundary.length < 3) {
        errors.boundary = 'Boundary must have at least 3 points';
      }
      return errors;
    };

    it('validates required sector_id field', () => {
      const errors = validateSectorForm({ sector_id: '', name: 'Test', boundary: [] });
      expect(errors.sector_id).toBe('Sector ID is required');
    });

    it('validates boundary minimum points', () => {
      const errors = validateSectorForm({
        sector_id: 'SECTOR-001',
        name: 'Test',
        boundary: [{ lat: 26.78, lng: -80.06 }, { lat: 26.77, lng: -80.05 }],
      });
      expect(errors.boundary).toBe('Boundary must have at least 3 points');
    });

    it('passes validation with valid polygon', () => {
      const errors = validateSectorForm({
        sector_id: 'SECTOR-001',
        name: 'Downtown',
        boundary: [
          { lat: 26.78, lng: -80.06 },
          { lat: 26.78, lng: -80.05 },
          { lat: 26.77, lng: -80.05 },
        ],
      });
      expect(Object.keys(errors)).toHaveLength(0);
    });
  });

  describe('User Form Validation', () => {
    const validateUserForm = (data: Record<string, unknown>, isNew: boolean) => {
      const errors: Record<string, string> = {};
      if (!data.username || String(data.username).trim() === '') {
        errors.username = 'Username is required';
      }
      if (!data.email || String(data.email).trim() === '') {
        errors.email = 'Email is required';
      } else if (!String(data.email).match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
        errors.email = 'Invalid email format';
      }
      if (!data.full_name || String(data.full_name).trim() === '') {
        errors.full_name = 'Full name is required';
      }
      if (!data.role) {
        errors.role = 'Role is required';
      }
      if (isNew && !data.password) {
        errors.password = 'Password is required for new users';
      }
      if (data.password && String(data.password).length < 8) {
        errors.password = 'Password must be at least 8 characters';
      }
      return errors;
    };

    it('validates required username', () => {
      const errors = validateUserForm({ username: '', email: 'test@test.com', full_name: 'Test', role: 'viewer' }, true);
      expect(errors.username).toBe('Username is required');
    });

    it('validates email format', () => {
      const errors = validateUserForm({ username: 'test', email: 'invalid', full_name: 'Test', role: 'viewer' }, true);
      expect(errors.email).toBe('Invalid email format');
    });

    it('validates password required for new users', () => {
      const errors = validateUserForm({ username: 'test', email: 'test@test.com', full_name: 'Test', role: 'viewer' }, true);
      expect(errors.password).toBe('Password is required for new users');
    });

    it('validates password minimum length', () => {
      const errors = validateUserForm({ username: 'test', email: 'test@test.com', full_name: 'Test', role: 'viewer', password: 'short' }, true);
      expect(errors.password).toBe('Password must be at least 8 characters');
    });

    it('does not require password for existing users', () => {
      const errors = validateUserForm({ username: 'test', email: 'test@test.com', full_name: 'Test', role: 'viewer' }, false);
      expect(errors.password).toBeUndefined();
    });
  });

  describe('Event Form Validation', () => {
    const validateEventForm = (data: Record<string, unknown>) => {
      const errors: Record<string, string> = {};
      if (!data.event_name || String(data.event_name).trim() === '') {
        errors.event_name = 'Event name is required';
      }
      if (!data.event_type) {
        errors.event_type = 'Event type is required';
      }
      if (!data.start_time) {
        errors.start_time = 'Start time is required';
      }
      if (!data.end_time) {
        errors.end_time = 'End time is required';
      }
      if (data.start_time && data.end_time) {
        if (new Date(String(data.start_time)) >= new Date(String(data.end_time))) {
          errors.end_time = 'End time must be after start time';
        }
      }
      const boundary = data.boundary as Array<{ lat: number; lng: number }> | undefined;
      if (!boundary || boundary.length < 3) {
        errors.boundary = 'Event boundary must have at least 3 points';
      }
      return errors;
    };

    it('validates end time after start time', () => {
      const errors = validateEventForm({
        event_name: 'Test Event',
        event_type: 'festival',
        start_time: '2024-12-20T18:00:00Z',
        end_time: '2024-12-20T10:00:00Z',
        boundary: [{ lat: 26.78, lng: -80.06 }, { lat: 26.78, lng: -80.05 }, { lat: 26.77, lng: -80.05 }],
      });
      expect(errors.end_time).toBe('End time must be after start time');
    });

    it('passes validation with valid event data', () => {
      const errors = validateEventForm({
        event_name: 'Riviera Beach Festival',
        event_type: 'festival',
        start_time: '2024-12-20T10:00:00Z',
        end_time: '2024-12-20T22:00:00Z',
        boundary: [
          { lat: 26.78, lng: -80.06 },
          { lat: 26.78, lng: -80.05 },
          { lat: 26.77, lng: -80.05 },
        ],
      });
      expect(Object.keys(errors)).toHaveLength(0);
    });
  });
});
