import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { remediationAPI, analysisAPI } from '../../services/api';

interface BulkRemediationProps {
  pdfIds?: string[];
}

const BulkRemediation: React.FC<BulkRemediationProps> = ({ pdfIds }) => {
  const [selectedIssueTypes, setSelectedIssueTypes] = useState<string[]>([]);
  const [selectedSeverities, setSelectedSeverities] = useState<string[]>([]);
  const [selectedRemediations, setSelectedRemediations] = useState<string[]>([]);
  const [showRemediationList, setShowRemediationList] = useState(false);
  
  const queryClient = useQueryClient();

  // Get bulk status
  const { data: bulkStatus } = useQuery({
    queryKey: ['remediation-bulk-status'],
    queryFn: async () => {
      const response = await remediationAPI.getBulkStatus();
      return response.data;
    },
    refetchInterval: 5000, // Poll every 5 seconds
  });

  // Bulk generation mutation
  const generateBulkMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await remediationAPI.generateBulk(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['remediation-bulk-status'] });
      alert('Bulk remediation generation started! Check back in a few moments.');
    },
    onError: (error) => {
      console.error('Bulk generation failed:', error);
      alert('Failed to start bulk remediation generation');
    },
  });

  // Bulk approval mutation
  const approveBulkMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await remediationAPI.approveBulk(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['remediation-bulk-status'] });
      setSelectedRemediations([]);
      alert('Bulk approval completed!');
    },
    onError: (error) => {
      console.error('Bulk approval failed:', error);
      alert('Failed to approve remediations');
    },
  });

  // Bulk implementation mutation
  const implementBulkMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await remediationAPI.implementBulk(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['remediation-bulk-status'] });
      alert('Bulk implementation started! Your PDFs will be fixed shortly.');
    },
    onError: (error) => {
      console.error('Bulk implementation failed:', error);
      alert('Failed to start bulk implementation');
    },
  });

  const handleGenerateBulk = () => {
    const data: any = {};
    
    if (pdfIds && pdfIds.length > 0) {
      data.pdf_ids = pdfIds;
    }
    
    if (selectedIssueTypes.length > 0) {
      data.issue_types = selectedIssueTypes;
    }
    
    if (selectedSeverities.length > 0) {
      data.severities = selectedSeverities;
    }
    
    generateBulkMutation.mutate(data);
  };

  const handleApproveBulk = (approved: boolean) => {
    if (selectedRemediations.length === 0) {
      alert('Please select remediations to approve/reject');
      return;
    }
    
    approveBulkMutation.mutate({
      remediation_ids: selectedRemediations,
      approved
    });
  };

  const handleImplementBulk = () => {
    const data: any = {};
    
    if (pdfIds && pdfIds.length > 0) {
      data.pdf_ids = pdfIds;
    }
    
    if (selectedIssueTypes.length > 0) {
      data.issue_types = selectedIssueTypes;
    }
    
    if (selectedSeverities.length > 0) {
      data.severities = selectedSeverities;
    }
    
    implementBulkMutation.mutate(data);
  };

  const issueTypes = [
    'missing_alt_text',
    'table_headers', 
    'reading_order',
    'missing_title',
    'color_contrast',
    'font_size'
  ];

  const severities = ['critical', 'high', 'medium', 'low'];

  const toggleArrayItem = (array: string[], item: string, setter: (items: string[]) => void) => {
    if (array.includes(item)) {
      setter(array.filter(i => i !== item));
    } else {
      setter([...array, item]);
    }
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-semibold mb-6">Bulk Remediation Management</h2>
      
      {/* Status Overview */}
      {bulkStatus && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <div className="bg-dark-700 rounded-lg p-4 text-center">
            <div className="text-sm text-gray-400">Total</div>
            <div className="text-2xl font-bold text-blue-500">{bulkStatus.total_remediations}</div>
          </div>
          <div className="bg-dark-700 rounded-lg p-4 text-center">
            <div className="text-sm text-gray-400">Pending</div>
            <div className="text-2xl font-bold text-yellow-500">{bulkStatus.status_breakdown.pending}</div>
          </div>
          <div className="bg-dark-700 rounded-lg p-4 text-center">
            <div className="text-sm text-gray-400">Approved</div>
            <div className="text-2xl font-bold text-green-500">{bulkStatus.status_breakdown.approved}</div>
          </div>
          <div className="bg-dark-700 rounded-lg p-4 text-center">
            <div className="text-sm text-gray-400">Pending Implementation</div>
            <div className="text-2xl font-bold text-orange-500">{bulkStatus.status_breakdown.pending_implementation}</div>
          </div>
          <div className="bg-dark-700 rounded-lg p-4 text-center">
            <div className="text-sm text-gray-400">Implemented</div>
            <div className="text-2xl font-bold text-green-600">{bulkStatus.status_breakdown.implemented}</div>
          </div>
        </div>
      )}

      {/* Bulk Generation */}
      <div className="space-y-6">
        <div className="border border-dark-700 rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Generate Remediations</h3>
          
          {/* Issue Type Filters */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Issue Types (optional)</label>
            <div className="flex flex-wrap gap-2">
              {issueTypes.map(type => (
                <button
                  key={type}
                  onClick={() => toggleArrayItem(selectedIssueTypes, type, setSelectedIssueTypes)}
                  className={`px-3 py-1 rounded-full text-sm ${
                    selectedIssueTypes.includes(type)
                      ? 'bg-primary-500 text-white'
                      : 'bg-dark-700 text-gray-300 hover:bg-dark-600'
                  }`}
                >
                  {type.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Severity Filters */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Severities (optional)</label>
            <div className="flex flex-wrap gap-2">
              {severities.map(severity => (
                <button
                  key={severity}
                  onClick={() => toggleArrayItem(selectedSeverities, severity, setSelectedSeverities)}
                  className={`px-3 py-1 rounded-full text-sm ${
                    selectedSeverities.includes(severity)
                      ? 'bg-primary-500 text-white'
                      : 'bg-dark-700 text-gray-300 hover:bg-dark-600'
                  }`}
                >
                  {severity}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleGenerateBulk}
            disabled={generateBulkMutation.isPending}
            className="btn-primary"
          >
            {generateBulkMutation.isPending ? 'Generating...' : 'Generate Bulk Remediations'}
          </button>
        </div>

        {/* Bulk Approval */}
        <div className="border border-dark-700 rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Manage Remediations</h3>
          
          <div className="flex gap-4 mb-4">
            <button
              onClick={() => setShowRemediationList(!showRemediationList)}
              className="btn-secondary"
            >
              {showRemediationList ? 'Hide' : 'Show'} Remediation List
            </button>
          </div>

          {showRemediationList && (
            <div className="mb-4 p-4 bg-dark-700 rounded-lg">
              <p className="text-sm text-gray-400 mb-2">
                Selected: {selectedRemediations.length} remediations
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setSelectedRemediations([])}
                  className="btn-secondary text-sm"
                >
                  Clear Selection
                </button>
                <button
                  onClick={() => {
                    // In a real implementation, you'd fetch actual remediation IDs
                    setSelectedRemediations(['all']);
                  }}
                  className="btn-secondary text-sm"
                >
                  Select All
                </button>
              </div>
            </div>
          )}

          <div className="flex gap-4">
            <button
              onClick={() => handleApproveBulk(true)}
              disabled={approveBulkMutation.isPending || selectedRemediations.length === 0}
              className="btn-primary"
            >
              {approveBulkMutation.isPending ? 'Approving...' : 'Approve Selected'}
            </button>
            <button
              onClick={() => handleApproveBulk(false)}
              disabled={approveBulkMutation.isPending || selectedRemediations.length === 0}
              className="btn-secondary"
            >
              Reject Selected
            </button>
          </div>
        </div>

        {/* Bulk Implementation */}
        <div className="border border-dark-700 rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Implement Fixes</h3>
          
          <p className="text-gray-400 mb-4">
            Apply approved remediations to your PDFs. This will create fixed versions of your documents.
          </p>

          <button
            onClick={handleImplementBulk}
            disabled={implementBulkMutation.isPending}
            className="btn-primary bg-green-600 hover:bg-green-700"
          >
            {implementBulkMutation.isPending ? 'Implementing...' : 'Implement All Approved Fixes'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default BulkRemediation;
