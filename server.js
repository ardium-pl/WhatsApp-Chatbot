import express from "express";
import axios from "axios";
import { config } from "dotenv";
import {
  HumanMessage,
  AIMessage,
  SystemMessage,
} from "@langchain/core/messages";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { RunnableSequence } from "@langchain/core/runnables";
import { ChatOpenAI } from "@langchain/openai";

// Create an express app
const app = express();
app.use(express.json());

// Load environment variables
config();
const {
  WEBHOOK_VERIFY_TOKEN,
  PHONE_NUMBER_ID,
  ACCESS_TOKEN,
  OPENAI_API_KEYPORT,
} = process.env;

const MESSAGE_HISTORY_LENGTH = 4;
const MODEL_OUTPUT_LENGTH = 5; // In words

// LangChain model
const model = new ChatOpenAI({
  model: "gpt-4o-mini",
  temperature: 0.2,
  maxTokens: 5,
});

// const chain = RunnableSequence.from([model, new StringOutputParser()]);

const taskWithHistory = new SystemMessage(
  `Answer using no more than ${MODEL_OUTPUT_LENGTH} words taking into account the following chat history.`
);

const taskWithoutHistory = new SystemMessage(
  `Answer using no more than ${MODEL_OUTPUT_LENGTH} words.`
);

let chatHistory = [];

async function generateAIresponse(messageContent) {
  const userQuestion = new HumanMessage(messageContent);
  let responseAI;

  if (chatHistory.length > 0) {
    responseAI = await model.invoke([
      taskWithHistory,
      ...chatHistory,
      userQuestion,
    ]);
  } else {
    responseAI = await model.invoke([taskWithoutHistory, userQuestion]);
  }

  // update chat history
  responseAI = new AIMessage(responseAI.content);

  if (chatHistory.length >= MESSAGE_HISTORY_LENGTH) {
    chatHistory.shift();
  }
  chatHistory.push(userQuestion);

  if (chatHistory.length >= MESSAGE_HISTORY_LENGTH) {
    chatHistory.shift();
  }
  chatHistory.push(responseAI);

  return responseAI.content;
}

//  Express routes
app.post("/webhook", async (req, res) => {
  const message = req.body.entry?.[0]?.changes?.[0]?.value?.messages?.[0];

  // Handle incoming text message
  if (message) {
    const senderPhoneNumber =
      req.body.entry?.[0]?.changes?.[0]?.value?.messages?.[0]?.from;

    // check if the incoming message contains text
    if (message?.type === "text") {
      const messageContent = message.text.body;

      console.log("Received a POST request containing a text message.");
      console.log(`Message text: ${messageContent}`);

      // Construct & send the response message
      const url = `https://graph.facebook.com/v20.0/${PHONE_NUMBER_ID}/messages`;

      try {
        const responseFromAI = generateAIresponse(messageContent);
      } catch (err) {
        const responseFromAI = "Error generating the response.";
      }

      const data = {
        messaging_product: "whatsapp",
        recipient_type: "individual",
        to: senderPhoneNumber,
        type: "text",
        text: {
          preview_url: false,
          body: responseFromAI, // Send back the AI response
        },
      };

      const config = {
        headers: {
          Authorization: `Bearer ${ACCESS_TOKEN}`,
          "Content-Type": "application/json",
        },
      };

      axios.post(url, data, config).catch((error) => {
        console.error(
          "Error sending message:",
          error.response ? error.response.data : error.message
        );
      });
    } else {
      console.log(
        `Received a POST request containing different type of message: {${message?.type}}.\n`
      );
    }
  } else {
    console.log("Received POST reqeust doesn't contain a message.\n");
  }
  res.sendStatus(200);
});

// accepts GET requests at the /webhook endpoint. You need this URL to setup webhook initially.
// info on verification request payload: https://developers.facebook.com/docs/graph-api/webhooks/getting-started#verification-requests
app.get("/webhook", (req, res) => {
  const mode = req.query["hub.mode"];
  const token = req.query["hub.verify_token"];
  const challenge = req.query["hub.challenge"];

  // check the mode and token sent are correct
  if (mode === "subscribe" && token === WEBHOOK_VERIFY_TOKEN) {
    // respond with 200 OK and challenge token from the request
    res.status(200).send(challenge);
    console.log("Webhook verified successfully!");
  } else {
    // respond with '403 Forbidden' if verify tokens do not match
    res.sendStatus(403);
    console.log("Webhook verification failed :(");
  }
});

app.get("/", (req, res) => {
  res.send(`<pre>
        Nothing to see here,
        check the logs :)
    </pre>`);
});

app.listen(PORT, () => {
  console.log(`Server is listening on port: ${PORT}`);
});
