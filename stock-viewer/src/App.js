import React, { useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import {
  Container,
  Grid,
  Paper,
  TextField,
  Button,
  CircularProgress,
  Typography,
  MenuItem,
  Select,
} from "@mui/material";

ChartJS.register(
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
  Legend
);

function App() {
  const [ticker, setTicker] = useState("AAPL");
  const [startDate, setStartDate] = useState("2024-06-01");
  const [endDate, setEndDate] = useState("2025-02-06");
  const [predictValue, setPredictValue] = useState(30);
  const [predictUnit, setPredictUnit] = useState("days"); // Default to days
  const [stockData, setStockData] = useState([]);
  const [predictionData, setPredictionData] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchStockData = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/stock?ticker=${ticker}&start=${startDate}&end=${endDate}&predict_days=${predictValue}&predict_unit=${predictUnit}`
      );
      const result = await response.json();
      setStockData(result.historicalData || []);
      setPredictionData(result.futurePredictions || []);
    } catch (error) {
      console.error("Error fetching stock data:", error);
    } finally {
      setLoading(false);
    }
  };

  // Prepare data for Chart.js (Historical Data)
  const historicalData = {
    labels: stockData.map((item) => new Date(item.date).toLocaleDateString()),
    datasets: [
      {
        label: `${ticker} Stock Price`,
        data: stockData.map((item) => item.close),
        borderColor: "blue",
        backgroundColor: "rgba(0, 0, 255, 0.1)",
        tension: 0.2,
      },
    ],
  };

  // Prepare data for Chart.js (Predictions)
  const predictions = {
    labels: predictionData.map((item) =>
      new Date(item.date).toLocaleDateString()
    ),
    datasets: [
      {
        label: `${ticker} Predicted Price`,
        data: predictionData.map((item) => item.predictedClose),
        borderColor: "green",
        backgroundColor: "rgba(0, 255, 0, 0.1)",
        tension: 0.2,
      },
    ],
  };

  return (
    <Container maxWidth="md">
      <Typography variant="h4" align="center" sx={{ my: 3 }}>
        Stock Price Viewer & Prediction
      </Typography>

      {/* Input Sections */}
      <Grid container spacing={3}>
        {/* Historical Data Inputs */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ padding: 3 }}>
            <Typography variant="h6">Fetch Historical Data</Typography>
            <TextField
              fullWidth
              label="Stock Ticker"
              variant="outlined"
              margin="normal"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
            />
            <TextField
              fullWidth
              label="Start Date"
              type="date"
              variant="outlined"
              margin="normal"
              InputLabelProps={{ shrink: true }}
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
            <TextField
              fullWidth
              label="End Date"
              type="date"
              variant="outlined"
              margin="normal"
              InputLabelProps={{ shrink: true }}
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </Paper>
        </Grid>

        {/* Prediction Inputs */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ padding: 3 }}>
            <Typography variant="h6">Predict Future Prices</Typography>
            <TextField
              fullWidth
              label="Prediction Range"
              type="number"
              variant="outlined"
              margin="normal"
              value={predictValue}
              onChange={(e) => setPredictValue(e.target.value)}
            />
            <Select
              fullWidth
              variant="outlined"
              value={predictUnit}
              onChange={(e) => setPredictUnit(e.target.value)}
            >
              <MenuItem value="days">Days</MenuItem>
              <MenuItem value="months">Months</MenuItem>
              <MenuItem value="years">Years</MenuItem>
            </Select>
          </Paper>
        </Grid>
      </Grid>

      {/* Fetch Button */}
      <Grid container justifyContent="center" sx={{ mt: 3 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={fetchStockData}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} color="inherit" /> : "Fetch Data"}
        </Button>
      </Grid>

      {/* Display Charts */}
      <Grid container spacing={3} sx={{ mt: 3 }}>
        {stockData.length > 0 && (
          <Grid item xs={12}>
            <Paper sx={{ padding: 3 }}>
              <Typography variant="h6">Historical Stock Prices</Typography>
              <Line data={historicalData} />
            </Paper>
          </Grid>
        )}

        {predictionData.length > 0 && (
          <Grid item xs={12}>
            <Paper sx={{ padding: 3 }}>
              <Typography variant="h6">Predicted Stock Prices</Typography>
              <Line data={predictions} />
            </Paper>
          </Grid>
        )}
      </Grid>
    </Container>
  );
}

export default App;
