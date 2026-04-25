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

export default function AlertLogPage() {
  const [historyData, setHistoryData] = React.useState<AlertHistoryItem[]>([]);

  React.useEffect(() => {
    const stored = localStorage.getItem('alert-history');

    if (stored) {
      setHistoryData(JSON.parse(stored));
    }
  }, []);

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
        </Box>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {historyData.length > 0 ? (
            historyData.map((entry) => (
              <Card
                key={entry.id}
                sx={{ backgroundColor: '#1f2937', borderColor: '#374151' }}
                className="border border-gray-700"
              >
                <CardContent className="p-6">
                  <Box className="flex items-start justify-between mb-4">
                    <Box>
                      <Typography className="text-white font-bold">
                        {entry.personName}
                      </Typography>
                      <Typography className="text-gray-400 text-sm">
                        {entry.timestamp}
                      </Typography>
                    </Box>

                    <Chip
                      label={entry.status}
                      color={
                        entry.status === 'Resolved'
                          ? 'success'
                          : entry.status === 'Escalated'
                          ? 'error'
                          : 'warning'
                      }
                      size="small"
                      icon={
                        entry.status === 'Resolved' ? (
                          <CheckCircleIcon />
                        ) : (
                          <WarningIcon />
                        )
                      }
                    />
                  </Box>

                  <Typography className="text-gray-300 mb-2">
                    Location: <span className="text-white">{entry.location}</span>
                  </Typography>

                  <Typography className="text-gray-400 mb-4">
                    {entry.notes}
                  </Typography>

                  <Button variant="outlined" fullWidth>
                    View Full Report
                  </Button>
                </CardContent>
              </Card>
            ))
          ) : (
            <Typography className="text-gray-400">
              No alert history yet.
            </Typography>
          )}
        </div>
      </Container>
    </div>
  );
}