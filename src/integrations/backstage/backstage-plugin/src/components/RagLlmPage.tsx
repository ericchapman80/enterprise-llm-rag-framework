import React, { useState, useEffect, useRef } from 'react';
import { useApi } from '@backstage/core-plugin-api';
import {
  Content,
  ContentHeader,
  Header,
  HeaderLabel,
  InfoCard,
  Page,
  Progress,
} from '@backstage/core-components';
import { Grid, Typography, TextField, Button, Divider, IconButton, Paper, Tooltip } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import SendIcon from '@material-ui/icons/Send';
import ThumbUpIcon from '@material-ui/icons/ThumbUp';
import ThumbDownIcon from '@material-ui/icons/ThumbDown';
import LinkIcon from '@material-ui/icons/Link';
import { ragLlmApiRef } from '../api';
import { QueryResponse, Source } from '../api/types';

const useStyles = makeStyles(theme => ({
  chatContainer: {
    height: 'calc(100vh - 200px)',
    display: 'flex',
    flexDirection: 'column',
  },
  messagesContainer: {
    flexGrow: 1,
    overflow: 'auto',
    padding: theme.spacing(2),
  },
  inputContainer: {
    display: 'flex',
    padding: theme.spacing(2),
    borderTop: `1px solid ${theme.palette.divider}`,
  },
  inputField: {
    flexGrow: 1,
  },
  sendButton: {
    marginLeft: theme.spacing(1),
  },
  userMessage: {
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.contrastText,
    borderRadius: '18px 18px 0 18px',
    padding: theme.spacing(1, 2),
    marginBottom: theme.spacing(1),
    maxWidth: '80%',
    alignSelf: 'flex-end',
  },
  botMessage: {
    backgroundColor: theme.palette.background.paper,
    borderRadius: '18px 18px 18px 0',
    padding: theme.spacing(1, 2),
    marginBottom: theme.spacing(1),
    maxWidth: '80%',
    alignSelf: 'flex-start',
    boxShadow: theme.shadows[1],
  },
  sourcesContainer: {
    marginTop: theme.spacing(1),
    padding: theme.spacing(1),
    backgroundColor: theme.palette.background.default,
    borderRadius: theme.shape.borderRadius,
  },
  sourceItem: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: theme.spacing(0.5),
  },
  feedbackContainer: {
    display: 'flex',
    justifyContent: 'flex-end',
    marginTop: theme.spacing(1),
  },
  feedbackButton: {
    marginLeft: theme.spacing(1),
  },
  messageContainer: {
    display: 'flex',
    flexDirection: 'column',
    marginBottom: theme.spacing(2),
  },
}));

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  sources?: Source[];
  conversationId?: string;
  feedbackGiven?: 'positive' | 'negative';
}

export const RagLlmPage = () => {
  const classes = useStyles();
  const ragLlmApi = useApi(ragLlmApiRef);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      isUser: true,
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response: QueryResponse = await ragLlmApi.query(input, conversationId);
      
      const botMessage: Message = {
        id: Date.now().toString() + '-response',
        text: response.response,
        isUser: false,
        sources: response.sources,
        conversationId: response.conversation_id,
      };

      setConversationId(response.conversation_id);
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error querying RAG LLM:', error);
      
      const errorMessage: Message = {
        id: Date.now().toString() + '-error',
        text: 'Sorry, I encountered an error processing your request. Please try again.',
        isUser: false,
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const handleFeedback = async (messageId: string, conversationId: string | undefined, isPositive: boolean) => {
    if (!conversationId) return;

    try {
      await ragLlmApi.submitFeedback({
        conversation_id: conversationId,
        query_id: messageId,
        rating: isPositive ? 1 : 0,
      });

      setMessages(prev =>
        prev.map(msg =>
          msg.id === messageId
            ? { ...msg, feedbackGiven: isPositive ? 'positive' : 'negative' }
            : msg
        )
      );
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  return (
    <Page themeId="tool">
      <Header title="AI Assistant" subtitle="Powered by RAG-enabled LLM">
        <HeaderLabel label="Owner" value="Engineering Effectiveness" />
      </Header>
      <Content>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <InfoCard title="Chat with AI Assistant" noPadding>
              <div className={classes.chatContainer}>
                <div className={classes.messagesContainer}>
                  {messages.map(message => (
                    <div key={message.id} className={classes.messageContainer}>
                      <Paper
                        className={message.isUser ? classes.userMessage : classes.botMessage}
                        elevation={0}
                      >
                        <Typography variant="body1">{message.text}</Typography>
                        
                        {message.sources && message.sources.length > 0 && (
                          <div className={classes.sourcesContainer}>
                            <Typography variant="caption" color="textSecondary">
                              Sources:
                            </Typography>
                            {message.sources.map((source, index) => (
                              <div key={index} className={classes.sourceItem}>
                                <Typography variant="caption" color="textSecondary">
                                  {source.url ? (
                                    <>
                                      <LinkIcon fontSize="small" />
                                      <a href={source.url} target="_blank" rel="noopener noreferrer">
                                        {source.title}
                                      </a>
                                    </>
                                  ) : (
                                    source.title
                                  )}
                                </Typography>
                              </div>
                            ))}
                          </div>
                        )}
                        
                        {!message.isUser && message.conversationId && (
                          <div className={classes.feedbackContainer}>
                            <Tooltip title="Helpful">
                              <IconButton
                                size="small"
                                className={classes.feedbackButton}
                                onClick={() => handleFeedback(message.id, message.conversationId, true)}
                                color={message.feedbackGiven === 'positive' ? 'primary' : 'default'}
                                disabled={!!message.feedbackGiven}
                              >
                                <ThumbUpIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Not Helpful">
                              <IconButton
                                size="small"
                                className={classes.feedbackButton}
                                onClick={() => handleFeedback(message.id, message.conversationId, false)}
                                color={message.feedbackGiven === 'negative' ? 'primary' : 'default'}
                                disabled={!!message.feedbackGiven}
                              >
                                <ThumbDownIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </div>
                        )}
                      </Paper>
                    </div>
                  ))}
                  {isLoading && <Progress />}
                  <div ref={messagesEndRef} />
                </div>
                <div className={classes.inputContainer}>
                  <TextField
                    className={classes.inputField}
                    placeholder="Ask a question..."
                    multiline
                    rowsMax={4}
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    variant="outlined"
                    disabled={isLoading}
                  />
                  <Button
                    className={classes.sendButton}
                    variant="contained"
                    color="primary"
                    endIcon={<SendIcon />}
                    onClick={handleSend}
                    disabled={isLoading || !input.trim()}
                  >
                    Send
                  </Button>
                </div>
              </div>
            </InfoCard>
          </Grid>
        </Grid>
      </Content>
    </Page>
  );
};
