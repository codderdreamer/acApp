const getTimeNum = (num: number) => {
  return num < 10 ? `0${num}` : num;
};

export const getTimeDifference = (startDate: Date) => {
  const endDate = new Date();

  const start = new Date(startDate);
  const end = new Date(endDate);
  const diff = end.getTime() - start.getTime();
  const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
  const minutes = Math.floor((diff / 1000 / 60) % 60);
  const seconds = Math.floor((diff / 1000) % 60);

  return `${getTimeNum(hours)}:${getTimeNum(minutes)}:${getTimeNum(seconds)}`;
};
