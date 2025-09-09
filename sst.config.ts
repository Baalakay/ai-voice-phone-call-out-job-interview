/// <reference path="./.sst/platform/config.d.ts" />

export default $config({
  app(input) {
    const stage = input?.stage || "dev";
    
    return {
      name: "gravywork",
      removal: stage === "production" ? "retain" : "remove",
      protect: stage === "production",
      home: "aws",
      providers: {
        aws: {
          region: "us-east-1",
          profile: "default",
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
      
      // Application resources
      processingFunction: application.processingFunction,
      assessmentApi: application.assessmentApi,
    };
  },
});