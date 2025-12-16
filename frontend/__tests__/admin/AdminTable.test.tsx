import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import AdminTable from '@/components/admin/AdminTable';

describe('AdminTable Component', () => {
  const mockColumns = [
    { key: 'name', label: 'Name' },
    { key: 'status', label: 'Status' },
    { key: 'type', label: 'Type' },
  ];

  const mockData = [
    { id: '1', name: 'Camera 1', status: 'active', type: 'fixed' },
    { id: '2', name: 'Camera 2', status: 'offline', type: 'ptz' },
    { id: '3', name: 'Camera 3', status: 'active', type: 'fixed' },
  ];

  it('renders table with columns and data', () => {
    render(
      <AdminTable
        columns={mockColumns}
        data={mockData}
        loading={false}
        onView={jest.fn()}
        canEdit={true}
        canDelete={true}
      />
    );

    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('Camera 1')).toBeInTheDocument();
    expect(screen.getByText('Camera 2')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(
      <AdminTable
        columns={mockColumns}
        data={[]}
        loading={true}
        onView={jest.fn()}
        canEdit={true}
        canDelete={true}
      />
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('shows empty message when no data', () => {
    render(
      <AdminTable
        columns={mockColumns}
        data={[]}
        loading={false}
        onView={jest.fn()}
        canEdit={true}
        canDelete={true}
        emptyMessage="No cameras found"
      />
    );

    expect(screen.getByText('No cameras found')).toBeInTheDocument();
  });

  it('filters data based on search input', () => {
    render(
      <AdminTable
        columns={mockColumns}
        data={mockData}
        loading={false}
        onView={jest.fn()}
        canEdit={true}
        canDelete={true}
        searchPlaceholder="Search cameras..."
      />
    );

    const searchInput = screen.getByPlaceholderText('Search cameras...');
    fireEvent.change(searchInput, { target: { value: 'Camera 1' } });

    expect(screen.getByText('Camera 1')).toBeInTheDocument();
    expect(screen.queryByText('Camera 2')).not.toBeInTheDocument();
  });

  it('calls onView when view button is clicked', () => {
    const mockOnView = jest.fn();
    render(
      <AdminTable
        columns={mockColumns}
        data={mockData}
        loading={false}
        onView={mockOnView}
        canEdit={true}
        canDelete={true}
      />
    );

    const viewButtons = screen.getAllByText('View');
    fireEvent.click(viewButtons[0]);

    expect(mockOnView).toHaveBeenCalledWith(mockData[0]);
  });

  it('calls onEdit when edit button is clicked', () => {
    const mockOnEdit = jest.fn();
    render(
      <AdminTable
        columns={mockColumns}
        data={mockData}
        loading={false}
        onView={jest.fn()}
        onEdit={mockOnEdit}
        canEdit={true}
        canDelete={true}
      />
    );

    const editButtons = screen.getAllByText('Edit');
    fireEvent.click(editButtons[0]);

    expect(mockOnEdit).toHaveBeenCalledWith(mockData[0]);
  });

  it('calls onDelete when delete button is clicked', () => {
    const mockOnDelete = jest.fn();
    render(
      <AdminTable
        columns={mockColumns}
        data={mockData}
        loading={false}
        onView={jest.fn()}
        onDelete={mockOnDelete}
        canEdit={true}
        canDelete={true}
      />
    );

    const deleteButtons = screen.getAllByText('Delete');
    fireEvent.click(deleteButtons[0]);

    expect(mockOnDelete).toHaveBeenCalledWith(mockData[0]);
  });

  it('hides edit button when canEdit is false', () => {
    render(
      <AdminTable
        columns={mockColumns}
        data={mockData}
        loading={false}
        onView={jest.fn()}
        onEdit={jest.fn()}
        canEdit={false}
        canDelete={true}
      />
    );

    expect(screen.queryByText('Edit')).not.toBeInTheDocument();
  });

  it('hides delete button when canDelete is false', () => {
    render(
      <AdminTable
        columns={mockColumns}
        data={mockData}
        loading={false}
        onView={jest.fn()}
        onDelete={jest.fn()}
        canEdit={true}
        canDelete={false}
      />
    );

    expect(screen.queryByText('Delete')).not.toBeInTheDocument();
  });

  it('renders boolean values correctly', () => {
    const dataWithBoolean = [
      { id: '1', name: 'Item 1', is_active: true },
      { id: '2', name: 'Item 2', is_active: false },
    ];
    const columnsWithBoolean = [
      { key: 'name', label: 'Name' },
      { key: 'is_active', label: 'Active' },
    ];

    render(
      <AdminTable
        columns={columnsWithBoolean}
        data={dataWithBoolean}
        loading={false}
        onView={jest.fn()}
        canEdit={true}
        canDelete={true}
      />
    );

    expect(screen.getByText('Yes')).toBeInTheDocument();
    expect(screen.getByText('No')).toBeInTheDocument();
  });

  it('handles pagination correctly', () => {
    const largeData = Array.from({ length: 25 }, (_, i) => ({
      id: String(i + 1),
      name: `Camera ${i + 1}`,
      status: 'active',
      type: 'fixed',
    }));

    render(
      <AdminTable
        columns={mockColumns}
        data={largeData}
        loading={false}
        onView={jest.fn()}
        canEdit={true}
        canDelete={true}
      />
    );

    expect(screen.getByText('Camera 1')).toBeInTheDocument();
    expect(screen.getByText('Camera 10')).toBeInTheDocument();
    expect(screen.queryByText('Camera 11')).not.toBeInTheDocument();

    const nextButton = screen.getByText('Next');
    fireEvent.click(nextButton);

    expect(screen.queryByText('Camera 1')).not.toBeInTheDocument();
    expect(screen.getByText('Camera 11')).toBeInTheDocument();
  });
});
