const cors = require("cors");
const express = require('express');
import {CosmosClient} from "@azure/cosmos";

const client = new CosmosClient({
  endpoint: "https://nosqldb-cosmos.documents.azure.com",
  key: "jVlAEu1e1eO6t6zkRs8XbKMQG7iEjtZcQ3UsujbKPVvnd00cw1JedIk1WfaDJL20VGXKUA06LMfaACDbJB6yJQ==",
});

// Create Express App and Routes
const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }))

// ACCEPTING CROSS SITE REQUESTS
app.use(cors());
app.use((req: any, res: any, next: Function)=>{
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

app.get('/parkslots', async (req: any, res: any) => {
  const data = await getParkSlots();
  res.status(200).send(data);
});

app.get('/parkslot/:id', async(req: any, res: any) => {
  const data = await getParkSlotByName(req.params.id);
  res.status(200).send(data);
});

app.get('/temperature/:id', async(req: any, res: any) => {
  const data = await getTemperatureByParkSlotName(req.params.id);
  res.status(200).send(data);
});

app.get('/humidity/:id', async(req: any, res: any) => {
  const data = await getHumidityByParkSlotName(req.params.id);
  res.status(200).send(data);
});

async function getParkSlotByName(id: string): Promise<any> {
  const container = client.database('iot-parking').container('parkslot');
  const results = await container.items
    .query({
      query: "SELECT top 1 * FROM parkslot WHERE parkslot.IoTHub.ConnectionDeviceId = @slotName ORDER BY parkslot._ts DESC",
      parameters: [{ name: "@slotName", value: 'parkslot' + id }]
    })
    .fetchAll();
  return results.resources.length === 0 ? null : results.resources[0];
}

async function getParkSlots(): Promise<Array<any>> {
  try {
    const container = client.database('iot-parking').container('parkslot');
    const results = await container.items.readAll().fetchAll();
    return results.resources;
  }
  catch (error) {
    console.error(error);
  }
  return [];
}

async function getTemperatureByParkSlotName(id: string): Promise<any> {
  const container = client.database('iot-parking').container('temperature');
  const results = await container.items
    .query({
      query: "SELECT top 1 * FROM temperature WHERE temperature.IoTHub.ConnectionDeviceId = @slotName ORDER BY temperature._ts DESC",
      parameters: [{ name: "@slotName", value: 'parkslot' + id }]
    })
    .fetchAll();
  return results.resources.length === 0 ? null : results.resources[0];
}

async function getHumidityByParkSlotName(id: string): Promise<any> {
  const container = client.database('iot-parking').container('humidity');
  const results = await container.items
    .query({
      query: "SELECT top 1 * FROM humidity WHERE humidity.IoTHub.ConnectionDeviceId = @slotName ORDER BY humidity._ts DESC",
      parameters: [{ name: "@slotName", value: 'parkslot' + id }]
    })
    .fetchAll();
  return results.resources.length === 0 ? null : results.resources[0];
}

export default {
  path: '/api',
  handler: app,
}
