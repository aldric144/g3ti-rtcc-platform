import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import {
  TextInput,
  NumberInput,
  DropdownSelect,
  ToggleSwitch,
  TextArea,
  MultiSelect,
  StatusBadge,
  getStatusVariant,
} from '@/components/admin/FormInputs';

describe('FormInputs Components', () => {
  describe('TextInput', () => {
    it('renders with label and value', () => {
      render(
        <TextInput
          label="Camera Name"
          name="name"
          value="Test Camera"
          onChange={jest.fn()}
        />
      );

      expect(screen.getByLabelText('Camera Name')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Test Camera')).toBeInTheDocument();
    });

    it('shows required indicator', () => {
      render(
        <TextInput
          label="Camera Name"
          name="name"
          value=""
          onChange={jest.fn()}
          required
        />
      );

      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('shows error message', () => {
      render(
        <TextInput
          label="Camera Name"
          name="name"
          value=""
          onChange={jest.fn()}
          error="Name is required"
        />
      );

      expect(screen.getByText('Name is required')).toBeInTheDocument();
    });

    it('calls onChange when value changes', () => {
      const mockOnChange = jest.fn();
      render(
        <TextInput
          label="Camera Name"
          name="name"
          value=""
          onChange={mockOnChange}
        />
      );

      const input = screen.getByLabelText('Camera Name');
      fireEvent.change(input, { target: { value: 'New Camera' } });

      expect(mockOnChange).toHaveBeenCalledWith('New Camera');
    });

    it('renders as disabled when disabled prop is true', () => {
      render(
        <TextInput
          label="Camera Name"
          name="name"
          value="Test"
          onChange={jest.fn()}
          disabled
        />
      );

      expect(screen.getByLabelText('Camera Name')).toBeDisabled();
    });
  });

  describe('NumberInput', () => {
    it('renders with label and value', () => {
      render(
        <NumberInput
          label="PSI"
          name="psi"
          value={65}
          onChange={jest.fn()}
        />
      );

      expect(screen.getByLabelText('PSI')).toBeInTheDocument();
      expect(screen.getByDisplayValue('65')).toBeInTheDocument();
    });

    it('respects min and max values', () => {
      render(
        <NumberInput
          label="PSI"
          name="psi"
          value={65}
          onChange={jest.fn()}
          min={0}
          max={100}
        />
      );

      const input = screen.getByLabelText('PSI');
      expect(input).toHaveAttribute('min', '0');
      expect(input).toHaveAttribute('max', '100');
    });

    it('calls onChange with number value', () => {
      const mockOnChange = jest.fn();
      render(
        <NumberInput
          label="PSI"
          name="psi"
          value={65}
          onChange={mockOnChange}
        />
      );

      const input = screen.getByLabelText('PSI');
      fireEvent.change(input, { target: { value: '75' } });

      expect(mockOnChange).toHaveBeenCalledWith(75);
    });
  });

  describe('DropdownSelect', () => {
    const options = [
      { value: 'fixed', label: 'Fixed' },
      { value: 'ptz', label: 'PTZ' },
      { value: 'dome', label: 'Dome' },
    ];

    it('renders with options', () => {
      render(
        <DropdownSelect
          label="Camera Type"
          name="type"
          value=""
          onChange={jest.fn()}
          options={options}
        />
      );

      expect(screen.getByLabelText('Camera Type')).toBeInTheDocument();
      expect(screen.getByText('Fixed')).toBeInTheDocument();
      expect(screen.getByText('PTZ')).toBeInTheDocument();
    });

    it('shows selected value', () => {
      render(
        <DropdownSelect
          label="Camera Type"
          name="type"
          value="ptz"
          onChange={jest.fn()}
          options={options}
        />
      );

      expect(screen.getByDisplayValue('PTZ')).toBeInTheDocument();
    });

    it('calls onChange when selection changes', () => {
      const mockOnChange = jest.fn();
      render(
        <DropdownSelect
          label="Camera Type"
          name="type"
          value=""
          onChange={mockOnChange}
          options={options}
        />
      );

      const select = screen.getByLabelText('Camera Type');
      fireEvent.change(select, { target: { value: 'dome' } });

      expect(mockOnChange).toHaveBeenCalledWith('dome');
    });
  });

  describe('ToggleSwitch', () => {
    it('renders with label', () => {
      render(
        <ToggleSwitch
          label="Active"
          name="is_active"
          checked={false}
          onChange={jest.fn()}
        />
      );

      expect(screen.getByText('Active')).toBeInTheDocument();
    });

    it('shows description when provided', () => {
      render(
        <ToggleSwitch
          label="Active"
          name="is_active"
          checked={false}
          onChange={jest.fn()}
          description="Enable this camera"
        />
      );

      expect(screen.getByText('Enable this camera')).toBeInTheDocument();
    });

    it('calls onChange when toggled', () => {
      const mockOnChange = jest.fn();
      render(
        <ToggleSwitch
          label="Active"
          name="is_active"
          checked={false}
          onChange={mockOnChange}
        />
      );

      const toggle = screen.getByRole('checkbox');
      fireEvent.click(toggle);

      expect(mockOnChange).toHaveBeenCalledWith(true);
    });
  });

  describe('TextArea', () => {
    it('renders with label and value', () => {
      render(
        <TextArea
          label="Notes"
          name="notes"
          value="Test notes"
          onChange={jest.fn()}
        />
      );

      expect(screen.getByLabelText('Notes')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Test notes')).toBeInTheDocument();
    });

    it('respects rows prop', () => {
      render(
        <TextArea
          label="Notes"
          name="notes"
          value=""
          onChange={jest.fn()}
          rows={5}
        />
      );

      const textarea = screen.getByLabelText('Notes');
      expect(textarea).toHaveAttribute('rows', '5');
    });
  });

  describe('MultiSelect', () => {
    const options = [
      { value: 'officer1', label: 'Officer 1' },
      { value: 'officer2', label: 'Officer 2' },
      { value: 'officer3', label: 'Officer 3' },
    ];

    it('renders with options', () => {
      render(
        <MultiSelect
          label="Assigned Officers"
          name="officers"
          value={[]}
          onChange={jest.fn()}
          options={options}
        />
      );

      expect(screen.getByText('Assigned Officers')).toBeInTheDocument();
    });

    it('shows selected values', () => {
      render(
        <MultiSelect
          label="Assigned Officers"
          name="officers"
          value={['officer1', 'officer2']}
          onChange={jest.fn()}
          options={options}
        />
      );

      expect(screen.getByText('Officer 1')).toBeInTheDocument();
      expect(screen.getByText('Officer 2')).toBeInTheDocument();
    });
  });

  describe('StatusBadge', () => {
    it('renders with correct variant for active status', () => {
      render(<StatusBadge status="active" />);
      expect(screen.getByText('active')).toBeInTheDocument();
    });

    it('renders with correct variant for offline status', () => {
      render(<StatusBadge status="offline" />);
      expect(screen.getByText('offline')).toBeInTheDocument();
    });
  });

  describe('getStatusVariant', () => {
    it('returns success for active/operational statuses', () => {
      expect(getStatusVariant('active')).toBe('success');
      expect(getStatusVariant('operational')).toBe('success');
      expect(getStatusVariant('online')).toBe('success');
    });

    it('returns warning for maintenance/pending statuses', () => {
      expect(getStatusVariant('maintenance')).toBe('warning');
      expect(getStatusVariant('pending')).toBe('warning');
      expect(getStatusVariant('charging')).toBe('warning');
    });

    it('returns error for offline/error statuses', () => {
      expect(getStatusVariant('offline')).toBe('error');
      expect(getStatusVariant('error')).toBe('error');
      expect(getStatusVariant('critical')).toBe('error');
    });

    it('returns default for unknown statuses', () => {
      expect(getStatusVariant('unknown')).toBe('default');
    });
  });
});
