module.exports = {
  preset: "ts-jest",
  testEnvironment: "node",
  roots: ["<rootDir>/../tests"],
  testMatch: ["**/*.test.ts"],
  moduleFileExtensions: ["ts", "js", "json"],
  moduleDirectories: ["node_modules", "<rootDir>/node_modules"],
  transform: {
    "^.+\\.ts$": [
      "ts-jest",
      { diagnostics: false },
    ],
  },
};

// 8e296a06
