import { get } from "../../../Services/client";
import headers from "../../../Services/headers.json";
import endpoints from "../../../Endpoints.json";

const config = headers.content_type.application_json;

export const GetUserWithToken = () => {
  return {
    data: {
      id: 1,
      username: "test",
    },
  };

  // return get(endpoints.PROFILE, config);
};
