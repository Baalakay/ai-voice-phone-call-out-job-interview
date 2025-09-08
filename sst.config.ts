/// <reference path="./.sst/platform/config.d.ts" />

import { projectConfig } from "./project.config";

export default $config({
  app(input) {
    const stage = input?.stage || "dev";
    const stageConfig = projectConfig.stages[stage as keyof typeof projectConfig.stages] || projectConfig.stages.dev;
    
    return {
      name: projectConfig.projectName,
      removal: stageConfig.removal,
      protect: stageConfig.protect,
      home: "aws",
      // Optional: Set region if specified in config
      providers: {
        aws: {
          region: projectConfig.aws.region,
          profile: projectConfig.aws.profile,
        },
      },
    };
  },
  async run() {
    const infra = await import("./infra/infrastructure");
    const app = await import("./infra/application");

    // Deploy infrastructure first
    const infrastructure = infra.InfrastructureStack();
    
    // Then deploy application that uses the infrastructure
    const application = app.ApplicationStack(infrastructure);

    return {
      // Infrastructure resources
      bucket: infrastructure.bucket,
      processingQueue: infrastructure.processingQueue,
      dataTable: infrastructure.dataTable,
      
      // Application resources
      processingFunction: application.processingFunction,
    };
  },
});