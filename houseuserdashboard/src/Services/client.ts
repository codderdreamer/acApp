import http from "./http";

export const get = (url: string, headers: any) => {
  return http.get(url, { headers });
};

export const post = (url: string, data: any, headers: any) => {
  return http.post(url, data, { headers });
};

export const patch = (url: string, data: any, headers: any) => {
  return http.patch(url, data, { headers });
};

export const put = (url: string, data: any, headers: any) => {
  return http.put(url, data, { headers });
};

export const deleteRequest = (url: string, headers: any) => {
  return http.delete(url, { headers });
};
