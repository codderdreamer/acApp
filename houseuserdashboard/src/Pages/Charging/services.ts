import headers from "../../Services/headers.json";
import endpoints from "../../Endpoints.json";
import { post } from "../../Services/client";

const config = headers.content_type.application_json;

export const StartCharge = (chargePointId: string, connectorId: string) => {
  return post(endpoints.STARTCHARGE, { chargePointId, connectorId }, config);
};

export const StopCharge = (chargePointId: string, transactionId: number) => {
  return post(endpoints.STARTCHARGE, { chargePointId, transactionId }, config);
};
