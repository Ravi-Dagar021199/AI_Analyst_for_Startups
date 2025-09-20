FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
COPY tsconfig.json ./
RUN npm install
COPY . .
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/serviceAccountKey.json
RUN npm run build
EXPOSE 8080
CMD ["npm", "run", "start"]