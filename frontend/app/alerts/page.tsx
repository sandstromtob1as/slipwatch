'use client';

import React from 'react';
import {
  Card,
  CardContent,
  Box,
  Typography,
  Container,
  Chip,
  Button,
} from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HistoryIcon from '@mui/icons-material/History';

interface AlertHistoryItem {
  id: string;
  personName: string;
  timestamp: string;
  location: string;
  status: 'Resolved' | 'Escalated' | 'Reviewed';
  notes: string;
}

const historyData: AlertHistoryItem[] = [
  {
    id: 'A-1024',
    personName: 'Ernest Brown',
    timestamp: '2025-04-23 19:05:12',
    location: 'Kitchen',
    status: 'Resolved',
    notes: 'Quick response team arrived and checked on the person. No injuries reported.',
  },
  {
    id: 'A-1025',
    personName: 'Helen Moore',
    timestamp: '2025-04-24 04:22:37',
    location: 'Hallway',
    status: 'Reviewed',
    notes: 'False-positive alert after a pet triggered the motion sensor. System sensitivity updated.',
  },
  {
    id: 'A-1026',
    personName: 'George King',
    timestamp: '2025-04-24 08:48:09',
    location: 'Bedroom',
    status: 'Escalated',
    notes: 'Medical team contacted after fall detection. Monitoring continues until clearance.',
  },
];

export default function AlertLogPage() {
  return (
    <div className="min-h-screen py-8">
      <Container maxWidth="lg">
        <Box className="mb-8">
          <Typography
            variant="h2"
            className="font-bold text-white mb-2 flex items-center gap-3"
          >
            <HistoryIcon className="text-blue-400" fontSize="large" />
            Alert Log History
          </Typography>
          <Typography variant="body1" className="text-gray-300">
            Review past fall events and incident outcomes. This history helps you verify system performance and follow up on resolved or escalated alerts.
          </Typography>
        </Box>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {historyData.map((entry) => (
            <div key={entry.id}>
              <Card sx={{ backgroundColor: '#1f2937', borderColor: '#374151' }} className="border border-gray-700 hover:border-gray-600 transition-colors">
                <CardContent className="p-6">
                  <Box className="flex items-start justify-between gap-4 mb-4">
                    <Box>
                      <Typography variant="h6" className="font-bold text-white">
                        {entry.personName}
                      </Typography>
                      <Typography variant="caption" className="text-gray-400">
                        {entry.timestamp}
                      </Typography>
                    </Box>
                    <Chip
                      label={entry.status}
                      color={entry.status === 'Resolved' ? 'success' : entry.status === 'Escalated' ? 'error' : 'warning'}
                      icon={entry.status === 'Resolved' ? <CheckCircleIcon /> : entry.status === 'Escalated' ? <WarningIcon /> : undefined}
                      size="small"
                    />
                  </Box>

                  <Typography variant="body2" className="text-gray-300 mb-3">
                    Location: <span className="text-white">{entry.location}</span>
                  </Typography>
                  <Typography variant="body2" className="text-gray-300 mb-4">
                    {entry.notes}
                  </Typography>
                  <Button variant="outlined" color="primary" fullWidth>
                    View Full Report
                  </Button>
                </CardContent>
              </Card>
            </div>
          ))}
        </div>
      </Container>
    </div>
  );
}
